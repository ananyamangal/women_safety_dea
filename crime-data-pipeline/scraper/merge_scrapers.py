import pandas as pd
import os

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# File paths
TOI_PATH = os.path.join(RAW_DIR, "toi.csv")
GOOGLE_PATH = os.path.join(RAW_DIR, "google_news.csv")

# ✅ Your synthetic dataset path
SYNTHETIC_PATH = os.path.join(PROCESSED_DIR, "delhi_crime_data.csv")

OUTPUT_PATH = os.path.join(RAW_DIR, "crime_news.csv")

# ---------------- SAFE READ ---------------- #

def safe_read(path, name):
    if not os.path.exists(path):
        print(f"⚠️ {name} file not found: {path}")
        return pd.DataFrame()

    if os.path.getsize(path) == 0:
        print(f"⚠️ {name} file is empty: {path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
        print(f"✅ Loaded {name}: {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌ Error reading {name}: {e}")
        return pd.DataFrame()

# ---------------- MAIN ---------------- #

def main():
    print("🔗 Merging datasets...")

    # Load all sources
    toi = safe_read(TOI_PATH, "TOI")
    google = safe_read(GOOGLE_PATH, "Google News")
    synthetic = safe_read(SYNTHETIC_PATH, "Synthetic")

    # Combine
    df = pd.concat([toi, google, synthetic], ignore_index=True)

    if df.empty:
        print("❌ No data to merge!")
        return

    print(f"\n📊 Total before cleaning: {len(df)}")

    # ---------------- CLEANING ---------------- #

    # Remove duplicates
    df = df.drop_duplicates(subset=["title"])

    # Drop rows with no title/description
    df = df.dropna(subset=["title", "description"], how="any")

    print(f"📊 After cleaning: {len(df)}")

    # Ensure consistent columns
    required_cols = ["title", "date", "description", "source_url"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[required_cols]

    # ---------------- SAVE ---------------- #

    os.makedirs(RAW_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Merged dataset created successfully!")
    print(f"📊 Final records: {len(df)}")
    print(f"📁 Saved at: {OUTPUT_PATH}")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()