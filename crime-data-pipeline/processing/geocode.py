import pandas as pd
from geopy.geocoders import Nominatim
import time
import os

# ✅ Initialize geocoder
geolocator = Nominatim(user_agent="delhi_crime_app")

# ✅ Cache to avoid repeated API calls
geo_cache = {}

# ✅ Convert location → lat/lon (with caching)
def get_lat_lon(place):
    place = str(place).lower().strip()

    # 🔹 Use cache (BIG speed improvement)
    if place in geo_cache:
        return geo_cache[place]

    try:
        location = geolocator.geocode(place + ", Delhi, India")

        if location:
            coords = (location.latitude, location.longitude)
            geo_cache[place] = coords
            return coords

    except Exception as e:
        print("❌ Error:", e)

    # 🔹 Fallback to Delhi center (VERY IMPORTANT)
    coords = (28.6139, 77.2090)  # Delhi default
    geo_cache[place] = coords
    return coords


def main():
    print("📂 Loading cleaned data...")

    try:
        df = pd.read_csv("data/processed/cleaned_data.csv")
    except FileNotFoundError:
        print("❌ cleaned_data.csv not found!")
        return

    if df.empty:
        print("⚠️ No data available for geocoding.")
        return

    print("🌍 Converting locations to coordinates...")

    latitudes = []
    longitudes = []

    # ✅ Unique locations only (MAJOR OPTIMIZATION)
    unique_locations = df["location"].unique()
    print(f"🔎 Unique locations found: {len(unique_locations)}")

    for i, loc in enumerate(unique_locations):
        print(f"[{i+1}] Geocoding: {loc}")

        lat, lon = get_lat_lon(loc)

        geo_cache[loc] = (lat, lon)

        time.sleep(1)  # avoid rate limiting

    # ✅ Map back to full dataframe
    df["latitude"] = df["location"].map(lambda x: geo_cache[x][0])
    df["longitude"] = df["location"].map(lambda x: geo_cache[x][1])

    # ❌ DO NOT DROP ROWS (IMPORTANT CHANGE)
    # df = df.dropna(subset=["latitude", "longitude"])

    # Save output
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/geocoded_data.csv", index=False)

    print(f"\n✅ Geocoded data saved to data/processed/geocoded_data.csv")
    print(f"📊 Total rows: {len(df)}")

    print("\nSample:")
    print(df.head())


if __name__ == "__main__":
    main()