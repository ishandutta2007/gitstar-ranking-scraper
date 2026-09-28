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
    and updates README.md with the table.
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
    
    readme_content = f"""# Gitstar Ranking - Top Users by Owned Repositories

Automated leaderboard showing the top 20 GitHub users from Gitstar Ranking ranked by the number of owned (source) repositories.

*Data Last Updated:* **{date_part}** (from `{filename}`)

## Top 20 Users by Owned Repositories (Sources Count)

{markdown_table}

---
*Generated automatically by `update_readme_leaderboard.py`.*
"""

    with open(README_FILE, mode="w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Successfully updated {README_FILE} with top 20 users!")

def main():
    latest_csv = get_latest_csv()
    if latest_csv:
        update_readme(latest_csv)

if __name__ == "__main__":
    main()
