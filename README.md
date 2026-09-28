# Gitstar Ranking Scraper & Leaderboard

A Python toolkit designed to scrape top GitHub user rankings from [Gitstar Ranking](https://gitstar-ranking.com/users), enrich user data with detailed repository metrics (owned vs. forked) via the GitHub REST API, and generate an automated leaderboard inside `README.md`.

All data files are automatically timestamped by year and month (`YYYY_Mon`), ensuring monthly historical tracking without data loss.

---

## Top 20 Users by Owned Repositories (Sources Count)

> **Last Updated:** `2026_Sep` (Extracted from `data/gitstar_users_with_repo_counts_2026_Sep.csv`)

| # | Username | Owned Repos (Sources) | Stars | Gitstar Profile |
| --- | --- | --- | --- | --- |
| 1 | [vim-scripts](https://gitstar-ranking.com/vim-scripts) | 5208 | 21667 | [Profile](https://gitstar-ranking.com/vim-scripts) |
| 2 | [Apress](https://gitstar-ranking.com/Apress) | 3560 | 46191 | [Profile](https://gitstar-ranking.com/Apress) |
| 3 | [mattn](https://gitstar-ranking.com/mattn) | 1157 | 58938 | [Profile](https://gitstar-ranking.com/mattn) |
| 4 | [sindresorhus](https://gitstar-ranking.com/sindresorhus) | 1130 | 1091868 | [Profile](https://gitstar-ranking.com/sindresorhus) |
| 5 | [camenduru](https://gitstar-ranking.com/camenduru) | 1074 | 38068 | [Profile](https://gitstar-ranking.com/camenduru) |
| 6 | [nirzaf](https://gitstar-ranking.com/nirzaf) | 975 | 22879 | [Profile](https://gitstar-ranking.com/nirzaf) |
| 7 | [keijiro](https://gitstar-ranking.com/keijiro) | 921 | 105582 | [Profile](https://gitstar-ranking.com/keijiro) |
| 8 | [jonschlinkert](https://gitstar-ranking.com/jonschlinkert) | 797 | 27131 | [Profile](https://gitstar-ranking.com/jonschlinkert) |
| 9 | [egoist](https://gitstar-ranking.com/egoist) | 756 | 79544 | [Profile](https://gitstar-ranking.com/egoist) |
| 10 | [mafintosh](https://gitstar-ranking.com/mafintosh) | 669 | 50503 | [Profile](https://gitstar-ranking.com/mafintosh) |
| 11 | [simonw](https://gitstar-ranking.com/simonw) | 653 | 66037 | [Profile](https://gitstar-ranking.com/simonw) |
| 12 | [IonicaBizau](https://gitstar-ranking.com/IonicaBizau) | 538 | 25489 | [Profile](https://gitstar-ranking.com/IonicaBizau) |
| 13 | [WebReflection](https://gitstar-ranking.com/WebReflection) | 528 | 26683 | [Profile](https://gitstar-ranking.com/WebReflection) |
| 14 | [LaravelDaily](https://gitstar-ranking.com/LaravelDaily) | 501 | 30648 | [Profile](https://gitstar-ranking.com/LaravelDaily) |
| 15 | [schollz](https://gitstar-ranking.com/schollz) | 472 | 78021 | [Profile](https://gitstar-ranking.com/schollz) |
| 16 | [mattdesl](https://gitstar-ranking.com/mattdesl) | 447 | 39214 | [Profile](https://gitstar-ranking.com/mattdesl) |
| 17 | [swyxio](https://gitstar-ranking.com/swyxio) | 447 | 26745 | [Profile](https://gitstar-ranking.com/swyxio) |
| 18 | [thlorenz](https://gitstar-ranking.com/thlorenz) | 432 | 21107 | [Profile](https://gitstar-ranking.com/thlorenz) |
| 19 | [max-mapper](https://gitstar-ranking.com/max-mapper) | 413 | 44631 | [Profile](https://gitstar-ranking.com/max-mapper) |
| 20 | [kentcdodds](https://gitstar-ranking.com/kentcdodds) | 403 | 54478 | [Profile](https://gitstar-ranking.com/kentcdodds) |

---

## Project Structure & Architecture

```
gitstar-ranking-scraper/
│
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

## Detailed Script Overview

### 1. `scrape_gitstar_users.py` (Stage 1: Web Scraper)
Scrapes user rankings directly from [https://gitstar-ranking.com/users](https://gitstar-ranking.com/users).
- **Target Pages:** First 10 pages (100 users per page = 1,000 top ranked users).
- **Extracted Fields:** `rank`, `username`, `stars`, `avatar_url`, `profile_url`.
- **Features:**
  - **Incremental Saving:** Flushes progress to CSV immediately after each page is scraped.
  - **Resume Support:** Skips already scraped usernames if interrupted.
  - **Timestamped Output:** Saves to `data/gitstar_users_top10pages_YYYY_Mon.csv`.

### 2. `fetch_user_repo_counts.py` (Stage 2: GitHub API Data Enrichment)
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

### 3. `update_readme_leaderboard.py` (Stage 3: README Leaderboard Generator)
Automates updating the leaderboard table inside `README.md`.
- **Features:**
  - **Auto-Discovery:** Automatically scans `data/` and identifies the latest CSV dataset by date suffix (`YYYY_Mon`).
  - **Sorting:** Sorts users descending by `sources_count`.
  - **Leaderboard Rendering:** Renders the Markdown table with links to profiles and updates `README.md`.

---

## Prerequisites & Installation

### Dependencies
- Python 3.8+
- `requests`
- `beautifulsoup4`

### Installation
```bash
pip install requests beautifulsoup4
```

### Environment Configuration (`.env`)
To avoid GitHub API rate limits (60 requests/hour unauthenticated vs. 5,000 requests/hour authenticated), configure your GitHub Personal Access Token in `.env`:

```env
ADMIN_TOKEN=github_pat_your_token_here
```

---

## How to Run the Pipeline

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

## Developer Guide & Maintenance

### Monthly Execution Workflow
Because all output files are automatically timestamped with `YYYY_Mon` (e.g., `2026_Sep`), running the pipeline each month creates a clean historical record inside `data/` without overwriting prior months.

### Modifying Scrape Scope
To change the number of pages scraped:
1. Open `scrape_gitstar_users.py`.
2. Update `num_pages`:
   ```python
   scrape_gitstar_users(num_pages=20)  # Scrape top 20 pages (2,000 users)
   ```

### Adjusting Batch Save Frequency
To change how frequently progress is written during repo count fetching:
1. Open `fetch_user_repo_counts.py`.
2. Modify `batch_size`:
   ```python
   process_users(batch_size=50)  # Flushes progress every 50 users
   ```

### Troubleshooting Rate Limits
If `fetch_user_repo_counts.py` encounters rate limit warnings:
- Verify `ADMIN_TOKEN` in `.env` is valid and active.
- Check token permissions (`public_repo` or fine-grained read access).

---
*Generated automatically by `update_readme_leaderboard.py`.*
