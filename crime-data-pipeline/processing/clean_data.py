import pandas as pd
import re
import os

# ---------------- PATH SETUP ---------------- #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "crime_news.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ---------------- CONSTANTS ---------------- #

DELHI_AREAS = [
    "rohini", "dwarka", "saket", "lajpat nagar",
    "karol bagh", "janakpuri", "pitampura",
    "connaught place", "cp", "vasant kunj",
    "hauz khas", "defence colony", "mayur vihar",
    "ashok vihar", "burari", "najafgarh",
    "patel nagar", "rajouri garden", "shahdara",

    # 🔥 Expanded coverage
    "wazirpur", "adarsh nagar", "model town",
    "kirti nagar", "tilak nagar", "seelampur",
    "okhla", "badarpur", "kalkaji", "narela",
    "sakarpur", "preet vihar", "geeta colony"
]

CRIME_MAP = {
    "Murder": ["murder", "killed", "shot", "stabbed", "hacked"],
    "Assault": ["rape", "assault", "harassment", "molest"],
    "Theft": ["theft", "robbery", "snatching", "looted"],
    "Kidnapping": ["kidnap", "abduct"],
    "Fraud": ["fraud", "scam", "cyber", "cheat"]
}

EXCLUDE_KEYWORDS = [
    "season", "review", "netflix", "trailer",
    "actor", "film", "series", "show", "ott"
]

# ---------------- CLEAN TEXT ---------------- #

def clean_text(text):
    text = str(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

# ---------------- FILTER ---------------- #

def is_valid(text):
    # ❌ Remove junk content
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False

    # ✅ Must contain crime-related keyword
    if any(word in text for words in CRIME_MAP.values() for word in words):
        return True

    return False

# ---------------- CLASSIFICATION ---------------- #

def classify_crime(text):
    for crime, keywords in CRIME_MAP.items():
        if any(word in text for word in keywords):
            return crime
    return "Other"

# ---------------- LOCATION EXTRACTION ---------------- #

def extract_location(title, description):
    title = str(title).lower()
    description = str(description).lower()

    # 🥇 Step 1: TITLE (most reliable)
    for loc in DELHI_AREAS:
        if loc in title:
            return loc

    # 🥈 Step 2: FULL ARTICLE TEXT
    for loc in DELHI_AREAS:
        if loc in description:
            return loc

    # 🥉 Step 3: fallback
    if "delhi" in title or "delhi" in description:
        return "delhi"

    return "delhi"

# ---------------- MAIN ---------------- #

def main():
    print("📂 Loading raw data...")

    if not os.path.exists(RAW_PATH):
        print("❌ Raw data not found!")
        return

    df = pd.read_csv(RAW_PATH)

    print(f"📊 Raw records: {len(df)}")

    # 🔹 Combine title + description (full article text already inside description)
    df["text"] = (
        df["title"].fillna("") + " " +
        df["description"].fillna("")
    )

    df["text"] = df["text"].apply(clean_text)

    print("🧹 Filtering valid crime articles...")
    df = df[df["text"].apply(is_valid)]

    print(f"📊 After filtering: {len(df)}")

    print("🧠 Extracting features...")

    df["crime_type"] = df["text"].apply(classify_crime)

    # 🔥 KEY FIX (title priority)
    df["location"] = df.apply(
        lambda x: extract_location(x["title"], x["description"]),
        axis=1
    )

    # Keep only useful columns
    df = df[
        ["title", "date", "description", "crime_type", "location", "source_url"]
    ]

    df = df.drop_duplicates(subset=["title"])

    if df.empty:
        print("⚠️ No data after cleaning.")
        return

    df.to_csv(OUTPUT_PATH, index=False)

    print("\n✅ Cleaned data saved")
    print(f"📊 Final records: {len(df)}")

    print("\n📍 Location distribution:")
    print(df["location"].value_counts().head(10))

    print("\n🔎 Crime types:")
    print(df["crime_type"].value_counts())

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()