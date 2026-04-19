from fastapi import FastAPI
import requests
import polyline
import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

app = FastAPI()
client = bigquery.Client()

GOOGLE_API_KEY ="AIzaSyDR_ND1HPaNcDRBHGqk2y2Htlr8FRT2Uso"

# ================= HOME =================
@app.get("/")
def home():
    return {"message": "Crime Safety API running 🚀"}


# ================= RISK =================
def get_risk(score):
    if score < 0.12:
        return "High Risk"
    elif score < 0.18:
        return "Medium Risk"
    else:
        return "Low Risk"


# ================= SAFETY =================
@app.get("/safety/{location}")
def get_safety(location: str):

    location = location.lower().strip()

    query = """
        SELECT 
            location,
            AVG(safety_score) as avg_score,
            COUNT(*) as incidents,
            ARRAY_AGG(crime_type LIMIT 5) as sample_crimes
        FROM `crimedatapipeline.crime_data.crime_scores`
        WHERE LOWER(location) = @location
        GROUP BY location
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("location", "STRING", location)
        ]
    )

    results = list(client.query(query, job_config=job_config).result())

    if not results:
        return {"message": "No data found"}

    row = results[0]

    return {
        "location": row.location,
        "safety_score": round(row.avg_score, 3),
        "risk_level": get_risk(row.avg_score),
        "incident_count": row.incidents,
        "sample_crimes": row.sample_crimes
    }


# ================= GOOGLE ROUTES =================
def get_routes(source, destination):

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline"
    }

    body = {
        "origin": {"address": source},
        "destination": {"address": destination},
        "travelMode": "WALK",
        "computeAlternativeRoutes": True
    }

    res = requests.post(url, json=body, headers=headers)

    print("Google API response:", res.json())  # DEBUG

    return res.json()


# ================= SAFE ROUTE =================
@app.get("/safe-route")
def safe_route(source: str, destination: str):

    print("Finding route:", source, "→", destination)

    data = get_routes(source, destination)
    routes = data.get("routes", [])

    if not routes:
        return {"error": "No routes found from Google API"}

    best_route = None
    lowest_risk = float("inf")

    for route in routes:

        encoded = route["polyline"]["encodedPolyline"]
        points = polyline.decode(encoded)

        # 🔥 Reduce points (performance fix)
        sampled_points = points[::25]

        coords = ",".join(
            [f"ST_GEOGPOINT({lon}, {lat})" for lat, lon in sampled_points]
        )

        query = f"""
        WITH route_points AS (
            SELECT point FROM UNNEST([{coords}]) AS point
        )
        SELECT AVG(safety_score) as score
        FROM `crimedatapipeline.crime_data.crime_scores`, route_points
        WHERE ST_DISTANCE(
            ST_GEOGPOINT(longitude, latitude),
            route_points.point
        ) < 500
        """

        result = list(client.query(query).result())

        avg_risk = result[0].score if result and result[0].score else 1

        print("Route risk:", avg_risk)

        if avg_risk < lowest_risk:
            lowest_risk = avg_risk
            best_route = route

    return {
        "route": best_route["polyline"]["encodedPolyline"],
        "risk_score": round(lowest_risk, 3)
    }