import csv
import os
import time
import requests

INPUT_CSV = "gitstar_users_top10pages.csv"
OUTPUT_CSV = "gitstar_users_with_repo_counts.csv"

def load_env_token():
    """Simple parser to read ADMIN_TOKEN from .env file if present."""
    token = os.environ.get("ADMIN_TOKEN")
    if token:
        return token
    if os.path.exists(".env"):
        with open(".env", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ADMIN_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

ADMIN_TOKEN = load_env_token()
use_authenticated = False

def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    if use_authenticated and ADMIN_TOKEN:
        headers["Authorization"] = f"token {ADMIN_TOKEN}"
    return headers

def make_request(url, timeout=10):
    """
    Make an HTTP GET request. If rate limited (403/429) and ADMIN_TOKEN is available,
    switch to authenticated headers and retry once.
    """
    global use_authenticated
    res = requests.get(url, headers=get_headers(), timeout=timeout)
    
    if res.status_code in (403, 429) and not use_authenticated and ADMIN_TOKEN:
        print(" Rate limit hit on unauthenticated request. Switching to ADMIN_TOKEN from .env...")
        use_authenticated = True
        res = requests.get(url, headers=get_headers(), timeout=timeout)
        
    return res

def get_user_repo_counts(username):
    """
    Fetch repository count metrics for a given username using GitHub REST API.
    Returns a dict with sources_count, forked_count, and total_repos_count.
    """
    page = 1
    sources_count = 0
    forked_count = 0
    total_repos_count = 0
    
    # Query user endpoint to get total public repos count
    user_url = f"https://api.github.com/users/{username}"
    try:
        res = make_request(user_url)
        if res.status_code == 200:
            user_info = res.json()
            total_repos_count = user_info.get("public_repos", 0)
        elif res.status_code in (403, 429):
            print(f" Rate limit exceeded even after fallback attempt for user {username}.")
        else:
            print(f" Non-200 response for {username} user info: {res.status_code}")
    except Exception as e:
        print(f" Error fetching profile for {username}: {e}")

    # Paginate through repos to count owned (source) vs forked repos
    while True:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        try:
            res = make_request(repos_url)
            if res.status_code != 200:
                if res.status_code not in (403, 429):
                    print(f" Warning: Failed to fetch repos page {page} for {username} (HTTP {res.status_code})")
                break
            
            repos = res.json()
            if not repos or not isinstance(repos, list):
                break

            for repo in repos:
                if repo.get("fork"):
                    forked_count += 1
                else:
                    sources_count += 1

            if len(repos) < 100:
                break
            page += 1
            time.sleep(0.2)
        except Exception as e:
            print(f" Error fetching repos for {username} page {page}: {e}")
            break

    if total_repos_count == 0 and (sources_count > 0 or forked_count > 0):
        total_repos_count = sources_count + forked_count

    return {
        "sources_count": sources_count,
        "forked_count": forked_count,
        "total_repos_count": total_repos_count
    }

def process_users():
    try:
        with open(INPUT_CSV, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found. Please run the first scraper first.")
        return

    fieldnames = list(rows[0].keys()) + ["sources_count", "forked_count", "total_repos_count"]
    
    updated_rows = []
    total_users = len(rows)

    print(f"Processing {total_users} users from {INPUT_CSV}...")
    
    for idx, row in enumerate(rows, start=1):
        username = row.get("username")
        print(f"[{idx}/{total_users}] Fetching repo counts for user: {username}...")
        
        counts = get_user_repo_counts(username)
        row.update(counts)
        updated_rows.append(row)
        
        time.sleep(0.5)

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"\nDone! Output saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_users()

