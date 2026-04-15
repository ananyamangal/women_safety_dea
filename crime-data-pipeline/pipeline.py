import subprocess

BUCKET = "crime-data-delhi-ananya"

def run_step(name, cmd):
    print(f"\n🚀 {name}")
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"❌ Failed: {name}")
        exit(1)

    print(f"✅ {name} completed")

def main():
    print("🔥 STARTING DATA PIPELINE 🔥")

    # 1️⃣ SCRAPING
    run_step("TOI Scraping", "python scraper/toi_scraper.py")
    run_step("Google Scraping", "python scraper/google_news_scraper.py")

    # 2️⃣ MERGE (IMPORTANT FIX)
    run_step("Merge Data", "python scraper/merge_scrapers.py")

    # 3️⃣ NOW EVERYTHING USES MERGED FILE
    run_step("Cleaning Data", "python processing/clean_data.py")
    run_step("Geocoding", "python processing/geocode.py")
    run_step("Safety Scoring", "python processing/safety_score.py")

    # 4️⃣ UPLOAD FINAL OUTPUT
    run_step(
        "Upload RAW",
        f"gcloud storage cp data/raw/crime_news.csv gs://{BUCKET}/raw/"
    )

    run_step(
        "Upload Processed",
        f"gcloud storage cp data/processed/final_data.csv gs://{BUCKET}/processed/"
    )

    print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()