import pandas as pd
from google.cloud import storage, bigquery
import subprocess
import os

BUCKET = "crime-data-delhi-ananya"
BQ_DATASET = "crime_data"

RAW_TABLE = "raw_news"

FILE_PATH = "/tmp/crime_news.csv"   # IMPORTANT (Cloud Run uses /tmp)


def run_step(name, cmd):
    print(f"\n🚀 {name}")
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"❌ Failed: {name}")
        exit(1)

    print(f"✅ {name} completed")


def upload_to_gcs():
    print("\n🚀 Uploading to GCS")
    client = storage.Client()
    bucket = client.bucket(BUCKET)
    blob = bucket.blob("raw/crime_news.csv")
    blob.upload_from_filename(FILE_PATH)
    print("✅ Upload complete")


def load_to_bigquery():
    print("\n🚀 Loading to BigQuery")
    client = bigquery.Client()

    table_id = f"{BQ_DATASET}.{RAW_TABLE}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
    )

    uri = f"gs://{BUCKET}/raw/crime_news.csv"

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()

    print("✅ Loaded to BigQuery")


def run_query(file_path):
    client = bigquery.Client()

    with open(file_path, "r") as f:
        query = f.read()

    job = client.query(query)
    job.result()

    print(f"✅ Ran {file_path}")


def main():
    print("🔥 STARTING CLOUD PIPELINE 🔥")

    # 1️⃣ SCRAPING
    run_step("TOI Scraping", "python scraper/toi_scraper.py")
    run_step("Google Scraping", "python scraper/google_news_scraper.py")

    # 2️⃣ MERGE
    run_step("Merge Data", "python scraper/merge_scrapers.py")

    # 3️⃣ UPLOAD TO GCS
    upload_to_gcs()

    # 4️⃣ LOAD TO BIGQUERY
    load_to_bigquery()

    # 5️⃣ TRANSFORM
    run_query("cloud/transform.sql")

    # 6️⃣ SAFETY SCORE
    run_query("cloud/safety_score.sql")

    print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()