# inside toi_scraper.py (ONLY TOI)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE_URL = "https://timesofindia.indiatimes.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

CRIME_KEYWORDS = [
    "murder", "killed", "robbed", "rape", "assault",
    "crime", "fraud", "theft", "snatching", "attack",
    "stabbed", "kidnap"
]

def get_article_links():
    url = "https://timesofindia.indiatimes.com/topic/delhi-crime"

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "articleshow" in href:
            full_link = href if href.startswith("http") else BASE_URL + href
            links.add(full_link)

    return list(links)


def scrape_article(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1")
    title = title.text.strip() if title else ""

    paragraphs = soup.find_all("p")
    description = " ".join([p.text.strip() for p in paragraphs])

    text = (title + " " + description).lower()

    if "delhi" not in text:
        return None

    if not any(word in text for word in CRIME_KEYWORDS):
        return None

    return {
        "title": title,
        "date": "",
        "description": description,
        "source_url": url
    }


def main():
    print("🔍 TOI scraping...")

    links = get_article_links()
    data = []

    for i, link in enumerate(links[:150]):
        print(f"[TOI {i+1}] {link}")

        article = scrape_article(link)
        if article:
            data.append(article)

        time.sleep(1)

    df = pd.DataFrame(data)

    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/toi.csv", index=False)

    print(f"✅ TOI saved ({len(df)}) articles")

    return df


if __name__ == "__main__":
    main()