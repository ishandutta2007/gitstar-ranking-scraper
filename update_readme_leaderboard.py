import csv
import glob
import os
import re
from datetime import datetime

DATA_DIR = "data"
README_FILE = "README.md"

# Regular expression to match filenames like gitstar_users_with_repo_counts_2026_Sep.csv
PATTERN = re.compile(r"gitstar_users_with_repo_counts_(\d{4})_([A-Za-z]{3})\.csv$")

def get_latest_csv():
    """
    Finds the latest CSV file in DATA_DIR matching the pattern gitstar_users_with_repo_counts_YYYY_Mon.csv
    based on the year and month parsed from the file name.
    """
    csv_files = glob.glob(os.path.join(DATA_DIR, "gitstar_users_with_repo_counts_*.csv"))
    
    dated_files = []
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        match = PATTERN.match(filename)
        if match:
            year, month_str = match.groups()
            try:
                dt = datetime.strptime(f"{year}_{month_str}", "%Y_%b")
                dated_files.append((dt, filepath))
            except ValueError:
                continue

    if not dated_files:
        print(f"No matching CSV files found in {DATA_DIR}.")
        return None

    # Sort by datetime descending
    dated_files.sort(key=lambda x: x[0], reverse=True)
    latest_file = dated_files[0][1]
    return latest_file

def generate_markdown_table(users):
    """
    Generates a Markdown table formatted for top 20 users by sources_count.
    """
    headers = ["#", "Username", "Owned Repos (Sources)", "Stars", "Gitstar Profile"]
    table_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |"
    ]
    
    for idx, user in enumerate(users, start=1):
        username = user.get("username", "")
        profile_url = user.get("profile_url", f"https://gitstar-ranking.com/{username}")
        sources_count = user.get("sources_count", 0)
        stars = user.get("stars", 0)
        
        # Render markdown row
        user_link = f"[{username}]({profile_url})"
        profile_link = f"[Profile]({profile_url})"
        table_lines.append(f"| {idx} | {user_link} | {sources_count} | {stars} | {profile_link} |")
        
    return "\n".join(table_lines)

def update_readme(latest_csv):
    """
    Reads user data from the latest CSV, extracts top 20 users by sources_count,
    and updates README.md with the table and comprehensive project documentation.
    """
    print(f"Reading data from latest CSV: {latest_csv}")
    
    users = []
    with open(latest_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["sources_count"] = int(row.get("sources_count", 0))
            except ValueError:
                row["sources_count"] = 0
            users.append(row)

    # Sort by sources_count descending
    users.sort(key=lambda u: u["sources_count"], reverse=True)
    top_20 = users[:20]

    filename = os.path.basename(latest_csv)
    date_part = filename.replace("gitstar_users_with_repo_counts_", "").replace(".csv", "")

    markdown_table = generate_markdown_table(top_20)
    
    readme_content = f"""<p align="center">
  <img src="assets/banner.svg" alt="Gitstar Ranking Scraper Banner" width="100%">
</p>

# 🌟 Gitstar Ranking Scraper & Leaderboard

<p align="center">
  <a href="https://github.com/ishandutta2007/Awesome-Awesome-Awesome"><img src="https://img.shields.io/badge/Awesome-%E2%9C%94-blueviolet?style=flat-square&logo=github" alt="Awesome"/></a>
  <a href="https://discord.gg/jc4xtF58Ve"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" /></a>
  <a href="https://github.com/ishandutta2007/gitstar-ranking-scraper"><img src="https://img.shields.io/github/stars/ishandutta2007/gitstar-ranking-scraper?style=social" alt="Stars" /></a>
  <a href="https://github.com/ishandutta2007/gitstar-ranking-scraper/fork"><img src="https://img.shields.io/github/forks/ishandutta2007/gitstar-ranking-scraper?style=social" alt="Forks" /></a>
  <a href="https://github.com/ishandutta2007"><img alt="GitHub followers" src="https://img.shields.io/github/followers/ishandutta2007?label=Follow" /></a>
</p>

A Python toolkit designed to scrape top GitHub user rankings from [Gitstar Ranking](https://gitstar-ranking.com/users), enrich user data with detailed repository metrics (owned vs. forked) via the GitHub REST API, and generate an automated leaderboard inside `README.md`.

All data files are automatically timestamped by year and month (`YYYY_Mon`), ensuring monthly historical tracking without data loss.

---

## 🏆 Top 20 Users by Owned Repositories (Sources Count)

> **Last Updated:** `{date_part}` (Extracted from `data/{filename}`)

{markdown_table}

---

## 🏗️ Project Structure & Architecture

```
gitstar-ranking-scraper/
│
├── assets/                                  # Project banners and visual assets
│   └── banner.svg
├── data/                                    # Output directory for timestamped CSV datasets
│   ├── gitstar_users_top10pages_2026_Sep.csv
│   └── gitstar_users_with_repo_counts_2026_Sep.csv
│
├── scrape_gitstar_users.py                 # Step 1: Scrapes top 10 pages from Gitstar Ranking
├── fetch_user_repo_counts.py              # Step 2: Enriches dataset with GitHub repo breakdown
├── update_readme_leaderboard.py           # Step 3: Updates README leaderboard table
│
├── .env                                     # Environment variables (GitHub ADMIN_TOKEN)
├── .gitignore                               # Specifies intentionally untracked files
└── README.md                                # Project documentation & leaderboard
```

---

## 📜 Detailed Script Overview

### 1. 🔍 `scrape_gitstar_users.py` (Stage 1: Web Scraper)
Scrapes user rankings directly from [https://gitstar-ranking.com/users](https://gitstar-ranking.com/users).
- **Target Pages:** First 10 pages (100 users per page = 1,000 top ranked users).
- **Extracted Fields:** `rank`, `username`, `stars`, `avatar_url`, `profile_url`.
- **Features:**
  - **Incremental Saving:** Flushes progress to CSV immediately after each page is scraped.
  - **Resume Support:** Skips already scraped usernames if interrupted.
  - **Timestamped Output:** Saves to `data/gitstar_users_top10pages_YYYY_Mon.csv`.

### 2. 📊 `fetch_user_repo_counts.py` (Stage 2: GitHub API Data Enrichment)
Enriches the scraped user list by fetching granular repository counts from the GitHub REST API.
- **Metrics Collected:**
  - `sources_count`: Owned / original repositories created by the user.
  - `forked_count`: Repositories forked from other projects.
  - `total_repos_count`: Total public repositories count.
- **Features:**
  - **Unauthenticated & Authenticated Fallback:** Starts with unauthenticated API calls. If rate limit HTTP `403`/`429` is reached, it seamlessly falls back to `ADMIN_TOKEN` loaded from `.env`.
  - **Batch Saving:** Saves progress to disk every 100 users.
  - **Resume Support:** Reads existing enriched dataset to avoid redundant API requests upon rerun.
  - **Timestamped Output:** Reads `data/gitstar_users_top10pages_YYYY_Mon.csv` and outputs `data/gitstar_users_with_repo_counts_YYYY_Mon.csv`.

### 3. 📝 `update_readme_leaderboard.py` (Stage 3: README Leaderboard Generator)
Automates updating the leaderboard table inside `README.md`.
- **Features:**
  - **Auto-Discovery:** Automatically scans `data/` and identifies the latest CSV dataset by date suffix (`YYYY_Mon`).
  - **Sorting:** Sorts users descending by `sources_count`.
  - **Leaderboard Rendering:** Renders the Markdown table with links to profiles and updates `README.md`.

---

## ⚙️ Prerequisites & Installation

### 📦 Dependencies
- Python 3.8+
- `requests`
- `beautifulsoup4`

### 💻 Installation
```bash
pip install requests beautifulsoup4
```

### 🔑 Environment Configuration (`.env`)
To avoid GitHub API rate limits (60 requests/hour unauthenticated vs. 5,000 requests/hour authenticated), configure your GitHub Personal Access Token in `.env`:

```env
ADMIN_TOKEN=github_pat_your_token_here
```

---

## 🚀 How to Run the Pipeline

Run the pipeline sequentially using standard Python:

```bash
# Step 1: Scrape top 10 pages from Gitstar Ranking
python scrape_gitstar_users.py

# Step 2: Fetch repo counts (owned vs forked) via GitHub API
python fetch_user_repo_counts.py

# Step 3: Update README.md leaderboard table
python update_readme_leaderboard.py
```

---

## 🛠️ Developer Guide & Maintenance

### 📅 Monthly Execution Workflow
Because all output files are automatically timestamped with `YYYY_Mon` (e.g., `2026_Sep`), running the pipeline each month creates a clean historical record inside `data/` without overwriting prior months.

### ⚙️ Modifying Scrape Scope
To change the number of pages scraped:
1. Open `scrape_gitstar_users.py`.
2. Update `num_pages`:
   ```python
   scrape_gitstar_users(num_pages=20)  # Scrape top 20 pages (2,000 users)
   ```

### ⚡ Adjusting Batch Save Frequency
To change how frequently progress is written during repo count fetching:
1. Open `fetch_user_repo_counts.py`.
2. Modify `batch_size`:
   ```python
   process_users(batch_size=50)  # Flushes progress every 50 users
   ```

### 🛑 Troubleshooting Rate Limits
If `fetch_user_repo_counts.py` encounters rate limit warnings:
- Verify `ADMIN_TOKEN` in `.env` is valid and active.
- Check token permissions (`public_repo` or fine-grained read access).

---

## ❤️ Support & Sponsorship

Thank you for checking out this project! If you find this toolkit useful, please consider supporting its ongoing development:

- 🌟 **Star this repository** to show your support!
- 🍴 **Fork it** to customize and add new features.
- 📢 **Share it** with your fellow developers and community!
- ☕ **Buy me a coffee / Sponsor:** Feel free to support via [GitHub Sponsors](https://github.com/sponsors/ishandutta2007).

---

## 📈 Star History

[![Star History Chart](https://star-history.dera.page/svg?repos=ishandutta2007/gitstar-ranking-scraper&type=date&legend=top-left)](https://star-history.dera.page/#ishandutta2007/gitstar-ranking-scraper&type=date&legend=top-left)

---
*Generated automatically by `update_readme_leaderboard.py`.*
"""

    # Ensure any occurrence of sindresorhus/awesome is replaced if present
    readme_content = readme_content.replace(
        "https://github.com/sindresorhus/awesome",
        "https://github.com/ishandutta2007/Awesome-Awesome-Awesome"
    )

    with open(README_FILE, mode="w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Successfully updated {README_FILE} with top 20 users!")



def main():
    latest_csv = get_latest_csv()
    if latest_csv:
        update_readme(latest_csv)

if __name__ == "__main__":
    main()
