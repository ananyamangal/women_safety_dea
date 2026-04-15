import pandas as pd
import os
from datetime import datetime

# ✅ Severity weights
severity_map = {
    "Murder": 5,
    "Assault": 4,
    "Kidnapping": 4,
    "Theft": 2,
    "Other": 1
}

# ✅ Compute recency weight
def compute_recency(date):
    if pd.isnull(date):
        return 1

    days_diff = (datetime.now() - date).days

    if days_diff < 7:
        return 5
    elif days_diff < 30:
        return 4
    elif days_diff < 90:
        return 3
    elif days_diff < 180:
        return 2
    else:
        return 1


def main():
    print("📂 Loading geocoded data...")

    df = pd.read_csv("data/processed/geocoded_data.csv")

    # ✅ Check empty early
    if df.empty:
        print("⚠️ No data available for safety scoring.")
        return

    # ✅ Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    print("⚖️ Calculating severity scores...")
    df["severity"] = df["crime_type"].map(severity_map).fillna(1)

    print("⏱️ Calculating recency weights...")
    df["recency"] = df["date"].apply(compute_recency)

    print("📊 Calculating crime frequency per location...")
    freq = df["location"].value_counts().to_dict()
    df["frequency"] = df["location"].map(freq)

    # ✅ Ensure numeric types (safe)
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce").fillna(1)
    df["recency"] = pd.to_numeric(df["recency"], errors="coerce").fillna(1)
    df["frequency"] = pd.to_numeric(df["frequency"], errors="coerce").fillna(1)

    print("🧠 Computing safety score...")

    alpha, beta, gamma = 0.5, 0.3, 0.2

    df["safety_score"] = 1 / (
        1
        + alpha * df["frequency"]
        + beta * df["severity"]
        + gamma * df["recency"]
    )

    df["safety_score"] = df["safety_score"].round(4)

    # ✅ Save output
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/final_data.csv", index=False)

    print("\n✅ Final dataset saved to data/processed/final_data.csv")
    print("\nSample data:")
    print(df.head())


if __name__ == "__main__":
    main()