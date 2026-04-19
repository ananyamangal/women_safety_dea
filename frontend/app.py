import streamlit as st
import requests
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

load_dotenv()

GOOGLE_API_KEY ="AIzaSyDR_ND1HPaNcDRBHGqk2y2Htlr8FRT2Uso"

st.set_page_config(layout="wide")
st.title("🛡️ Smart Crime Safety & Route System")

menu = st.sidebar.radio(
    "Choose Feature",
    ["🚨 Crime Safety Checker", "🛣️ Safe Route Finder"]
)

# ================= MAP =================
def render_map(polyline_str):

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_API_KEY}&libraries=geometry"></script>
    </head>
    <body>
    <div id="map" style="height:500px;"></div>

    <script>
    function initMap() {{

        const map = new google.maps.Map(document.getElementById("map"), {{
            zoom: 13,
            center: {{ lat: 28.6139, lng: 77.2090 }}
        }});

        const path = google.maps.geometry.encoding.decodePath("{polyline_str}");

        const route = new google.maps.Polyline({{
            path: path,
            geodesic: true,
            strokeColor: "#FF0000",
            strokeWeight: 4
        }});

        route.setMap(map);

        const bounds = new google.maps.LatLngBounds();
        path.forEach(p => bounds.extend(p));
        map.fitBounds(bounds);

        new google.maps.Marker({{ position: path[0], map: map, label: "S" }});
        new google.maps.Marker({{ position: path[path.length-1], map: map, label: "D" }});
    }}

    initMap();
    </script>

    </body>
    </html>
    """

    components.html(html, height=520)


# ================= SAFETY =================
if menu == "🚨 Crime Safety Checker":

    location = st.text_input("Enter Location")

    if location:
        res = requests.get(f"http://127.0.0.1:8000/safety/{location}")

        if res.status_code != 200:
            st.error("Backend error")
        else:
            data = res.json()

            if "message" in data:
                st.error(data["message"])
            else:
                st.success(f"📍 {data['location']}")
                st.metric("Safety Score", data["safety_score"])
                st.metric("Risk Level", data["risk_level"])
                st.metric("Incidents", data["incident_count"])

                st.subheader("Sample Crimes")
                for c in data["sample_crimes"]:
                    st.write("•", c)


# ================= ROUTE =================
elif menu == "🛣️ Safe Route Finder":

    source = st.text_input("Enter Source")
    destination = st.text_input("Enter Destination")

    if source and destination:

        with st.spinner("Finding safest route..."):

            try:
                res = requests.get(
                    f"http://127.0.0.1:8000/safe-route?source={source}&destination={destination}",
                    timeout=20
                )

                data = res.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    render_map(data["route"])
                    st.success(f"Route Safety Score: {data['risk_score']}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Try shorter distance.")
            except Exception as e:
                st.error("Something went wrong")
                st.write(e)