import csv
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://gitstar-ranking.com/users"
OUTPUT_CSV = "gitstar_users_top10pages.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_gitstar_users(num_pages=10):
    users_data = []

    for page in range(1, num_pages + 1):
        url = f"{BASE_URL}?page={page}"
        print(f"Scraping page {page}: {url}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("a", class_="paginated_item")

        for item in items:
            # Extract Rank and Username
            name_span = item.find("span", class_="name")
            rank = None
            username = None

            if name_span:
                # Text inside name_span typically contains rank (e.g. "1.") followed by hidden-xs hidden-sm span with username
                text_parts = name_span.get_text(strip=True, separator=" ").split()
                if text_parts:
                    rank = text_parts[0].rstrip(".")
                
                user_span = name_span.find("span", class_="hidden-xs hidden-sm")
                if user_span:
                    username = user_span.get_text(strip=True)
                elif len(text_parts) > 1:
                    username = text_parts[1]

            # Extract Stars Count
            stars_span = item.find("span", class_="stargazers_count")
            stars = stars_span.get_text(strip=True) if stars_span else None
            # Clean stars count if needed (e.g. integer conversion or string)
            if stars:
                stars = stars.replace(",", "")

            # Extract Avatar URL
            img_tag = item.find("img", class_="avatar_image_big")
            avatar_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

            # Extract Profile URL
            user_link = item.get("href")
            profile_url = f"https://gitstar-ranking.com{user_link}" if user_link else None

            if username:
                users_data.append({
                    "rank": rank,
                    "username": username,
                    "stars": stars,
                    "avatar_url": avatar_url,
                    "profile_url": profile_url
                })

        time.sleep(1)  # Respectful delay between requests

    return users_data

def save_to_csv(data, filename):
    if not data:
        print("No data collected.")
        return

    fieldnames = ["rank", "username", "stars", "avatar_url", "profile_url"]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Successfully saved {len(data)} users to {filename}")

if __name__ == "__main__":
    data = scrape_gitstar_users(10)
    save_to_csv(data, OUTPUT_CSV)
