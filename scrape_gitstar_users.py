import csv
import os
import time
import requests
from bs4 import BeautifulSoup

DATA_DIR = "data"
BASE_URL = "https://gitstar-ranking.com/users"
OUTPUT_CSV = os.path.join(DATA_DIR, "gitstar_users_top10pages.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
FIELDNAMES = ["rank", "username", "stars", "avatar_url", "profile_url"]


def save_to_csv(data, filename):
    if not data:
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)


def load_existing_data(filename):
    existing_data = []
    scraped_usernames = set()
    if os.path.exists(filename):
        try:
            with open(filename, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_data.append(row)
                    if row.get("username"):
                        scraped_usernames.add(row["username"])
            print(f"Resuming: Loaded {len(existing_data)} existing records from {filename}.")
        except Exception as e:
            print(f"Warning: Failed to read existing {filename} ({e}). Starting fresh.")
    return existing_data, scraped_usernames

def scrape_gitstar_users(num_pages=10, filename=OUTPUT_CSV):
    users_data, scraped_usernames = load_existing_data(filename)

    for page in range(1, num_pages + 1):
        url = f"{BASE_URL}?page={page}"
        print(f"Scraping page {page}/{num_pages}: {url}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("a", class_="paginated_item")

        new_items_added = 0
        for item in items:
            # Extract Rank and Username
            name_span = item.find("span", class_="name")
            rank = None
            username = None

            if name_span:
                text_parts = name_span.get_text(strip=True, separator=" ").split()
                if text_parts:
                    rank = text_parts[0].rstrip(".")
                
                user_span = name_span.find("span", class_="hidden-xs hidden-sm")
                if user_span:
                    username = user_span.get_text(strip=True)
                elif len(text_parts) > 1:
                    username = text_parts[1]

            if not username or username in scraped_usernames:
                continue

            # Extract Stars Count
            stars_span = item.find("span", class_="stargazers_count")
            stars = stars_span.get_text(strip=True) if stars_span else None
            if stars:
                stars = stars.replace(",", "")

            # Extract Avatar URL
            img_tag = item.find("img", class_="avatar_image_big")
            avatar_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

            # Extract Profile URL
            user_link = item.get("href")
            profile_url = f"https://gitstar-ranking.com{user_link}" if user_link else None

            users_data.append({
                "rank": rank,
                "username": username,
                "stars": stars,
                "avatar_url": avatar_url,
                "profile_url": profile_url
            })
            scraped_usernames.add(username)
            new_items_added += 1

        # Save progress immediately after scraping each page
        save_to_csv(users_data, filename)
        print(f" Saved page {page} ({new_items_added} new users added, total: {len(users_data)}) to {filename}")

        time.sleep(1)  # Respectful delay between requests

    print(f"\nDone! Finished scraping {num_pages} pages. Total records: {len(users_data)}")

if __name__ == "__main__":
    scrape_gitstar_users(num_pages=10)

