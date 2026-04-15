import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# ---------------- CONFIG ---------------- #

RSS_URL = "https://news.google.com/rss/search?q=delhi+crime"
HEADERS = {"User-Agent": "Mozilla/5.0"}

CRIME_KEYWORDS = [
    "murder", "killed", "robbed", "rape", "assault",
    "crime", "fraud", "theft", "snatching", "attack",
    "stabbed", "kidnap", "cyber", "scam", "shoot"
]

EXCLUDE_KEYWORDS = [
    "season", "review", "netflix", "trailer",
    "actor", "film", "series", "show", "ott",
    "episode", "movie", "web series"
]

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(RAW_DIR, exist_ok=True)

# ---------------- SCRAPER ---------------- #

def scrape_article(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join([p.text for p in paragraphs])

        return text[:3000]
    except:
        return ""

# ---------------- FILTER ---------------- #

def is_valid_article(title, description):
    text = (title + " " + description).lower()

    # ❌ Remove entertainment junk
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False

    # ✅ Keep if ANY crime keyword present (RELAXED)
    if any(word in text for word in CRIME_KEYWORDS):
        return True

    return False

# ---------------- MAIN ---------------- #

def main():
    print("📰 Google News scraping (robust)...")

    feed = feedparser.parse(RSS_URL)
    data = []

    total = 0
    valid = 0

    for i, entry in enumerate(feed.entries[:100]):
        total += 1
        print(f"[GN {i+1}] {entry.title}")

        title = entry.title
        date = entry.get("published", "")
        url = entry.link

        description = scrape_article(url)

        # ✅ fallback if scraping fails
        if not description:
            description = title

        # ✅ filter
        if not is_valid_article(title, description):
            continue

        valid += 1

        data.append({
            "title": title,
            "date": date,
            "description": description,
            "source_url": url
        })

        time.sleep(1)

    print(f"\n📊 Total scraped: {total}")
    print(f"✅ Valid articles: {valid}")

    # ✅ HANDLE EMPTY DATA (CRITICAL FIX)
    if not data:
        print("⚠️ No valid articles found — creating empty structured file")

        df = pd.DataFrame(columns=[
            "title", "date", "description", "source_url"
        ])
    else:
        df = pd.DataFrame(data)

    file_path = os.path.join(RAW_DIR, "google_news.csv")
    df.to_csv(file_path, index=False)

    print(f"\n✅ Google News saved ({len(df)} articles)")
    print(f"📁 Path: {file_path}")

    return df

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()