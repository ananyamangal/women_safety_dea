import pandas as pd
import os

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local fallback paths (works locally)
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

TOI_PATH = os.path.join(RAW_DIR, "toi.csv")
GOOGLE_PATH = os.path.join(RAW_DIR, "google_news.csv")
SYNTHETIC_PATH = os.path.join(PROCESSED_DIR, "delhi_crime_data.csv")

# ✅ CLOUD-SAFE OUTPUT (IMPORTANT)
OUTPUT_PATH = "/tmp/crime_news.csv"


# ---------------- SAFE READ ---------------- #

def safe_read(path, name):
    if not os.path.exists(path):
        print(f"⚠️ {name} not found: {path}")
        return pd.DataFrame()

    if os.path.getsize(path) == 0:
        print(f"⚠️ {name} is empty: {path}")
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

    toi = safe_read(TOI_PATH, "TOI")
    google = safe_read(GOOGLE_PATH, "Google News")
    synthetic = safe_read(SYNTHETIC_PATH, "Synthetic")

    df = pd.concat([toi, google, synthetic], ignore_index=True)

    if df.empty:
        print("❌ No data found from any source!")
        return

    print(f"\n📊 Before cleaning: {len(df)} rows")

    # ---------------- COLUMN SAFETY ---------------- #

    required_cols = ["title", "date", "description", "source_url"]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Ensure no NaN crashes
    df = df.fillna("")

    # ---------------- CLEANING ---------------- #

    # Drop rows without meaningful content
    df = df[df["title"].str.strip() != ""]
    df = df[df["description"].str.strip() != ""]

    # Safe deduplication
    df = df.drop_duplicates(subset=["title", "source_url"], keep="first")

    print(f"📊 After cleaning: {len(df)} rows")

    # Keep only required columns
    df = df[required_cols]

    # ---------------- SAVE ---------------- #

    os.makedirs("/tmp", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("\n✅ Merged dataset created successfully!")
    print(f"📁 Saved at: {OUTPUT_PATH}")
    print(f"📊 Final records: {len(df)}")


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()