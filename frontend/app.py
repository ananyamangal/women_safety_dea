import streamlit as st
import requests

st.title("🚨 Delhi Crime Safety Checker")

location = st.text_input("Enter Location")

if location:
    location = location.lower().strip()

    url = f"http://127.0.0.1:8000/safety/{location}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # ❌ Handle no data case
        if "message" in data:
            st.error(data["message"])
            if "suggestion" in data:
                st.info(data["suggestion"])

        else:
            st.success(f"📍 Location: {data['location']}")

            st.metric("Safety Score", data["safety_score"])
            st.metric("Risk Level", data["risk_level"])
            st.metric("Incidents", data["incident_count"])

            st.subheader("🔎 Sample Crimes")
            for crime in data["sample_crimes"]:
                st.write(f"- {crime}")

    else:
        st.error("❌ API Error")