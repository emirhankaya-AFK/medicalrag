import streamlit as st
import requests
from ..components.auth_guard import check_auth
from ..components.timeline_chart import render_timeline

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Patient History Timeline - MedicalRAG", layout="wide")

check_auth(allowed_roles=["doctor", "nurse", "patient"])

st.title("📅 Patient Chronology Timeline")
st.write("Visual chronological history compiled from all uploaded patient reports, labs, and diagnoses.")

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# Fetch patients
patients = []
try:
    if st.session_state["role"] == "patient":
        p_id = st.number_input("Enter your Patient ID:", min_value=1, step=1, value=1)
        pat_res = requests.get(f"{BACKEND_URL}/records/patient/{p_id}", headers=headers)
        if pat_res.status_code == 200:
            patients = [pat_res.json()]
    else:
        pat_res = requests.get(f"{BACKEND_URL}/records/patient", headers=headers)
        if pat_res.status_code == 200:
            patients = pat_res.json()
except Exception as e:
    st.error(f"Error fetching patient information: {e}")

if not patients:
    st.info("No patient profiles available.")
else:
    patient_options = {f"{pat['name']} (ID: {pat['id']})": pat["id"] for pat in patients}
    selected_patient = st.selectbox("Select Patient Profile", list(patient_options.keys()))
    selected_patient_id = patient_options[selected_patient]
    
    with st.spinner("Compiling chronology chart..."):
        try:
            res = requests.get(f"{BACKEND_URL}/extraction/patient/{selected_patient_id}/timeline", headers=headers)
            if res.status_code == 200:
                timeline_events = res.json()
                render_timeline(timeline_events)
            else:
                st.error("Failed to compile patient timeline.")
        except Exception as e:
            st.error(f"Failed to query backend: {e}")
