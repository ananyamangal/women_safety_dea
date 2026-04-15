from fastapi import FastAPI
from google.cloud import bigquery

app = FastAPI()

client = bigquery.Client()

# ---------------- HOME ---------------- #

@app.get("/")
def home():
    return {"message": "Crime Safety API running 🚀"}


# ---------------- HELPER ---------------- #

def get_risk(score):
    if score < 0.12:
        return "High Risk"
    elif score < 0.18:
        return "Medium Risk"
    else:
        return "Low Risk"


# ---------------- MAIN API ---------------- #

@app.get("/safety/{location}")
def get_safety(location: str):

    # ✅ Clean input
    location = location.lower().strip()

    # ❗ safer query (prevents weird matching issues)
    query = f"""
        SELECT 
            location,
            AVG(safety_score) as avg_score,
            COUNT(*) as incidents,
            ARRAY_AGG(crime_type LIMIT 5) as sample_crimes
        FROM `crimedatapipeline.crime_data.crime_scores`
        WHERE LOWER(location) = '{location}'
        GROUP BY location
    """

    results = list(client.query(query).result())

    # ❌ No data case
    if not results:
        return {
            "location": location,
            "message": "No data found",
            "suggestion": "Try areas like dwarka, rohini, saket, lajpat nagar"
        }

    row = results[0]

    score = round(row.avg_score, 3)

    return {
        "location": row.location,
        "safety_score": score,
        "risk_level": get_risk(score),
        "incident_count": row.incidents,
        "sample_crimes": row.sample_crimes
    }