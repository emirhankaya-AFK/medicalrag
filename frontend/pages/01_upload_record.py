import streamlit as st
import requests
from ..components.auth_guard import check_auth
from ..components.record_viewer import render_record_card

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Manage Patient Records - MedicalRAG", layout="wide")

# Auth Check: Doctors and Nurses only
check_auth(allowed_roles=["doctor", "nurse"])

st.title("🗂️ Patient Profile & Records Management")

tab1, tab2 = st.tabs(["📝 Add Patient Profile", "📤 Upload Medical Record"])

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# Fetch Patients list
patients = []
try:
    pat_res = requests.get(f"{BACKEND_URL}/records/patient", headers=headers)
    if pat_res.status_code == 200:
        patients = pat_res.json()
except Exception as e:
    st.error(f"Error fetching patient profiles: {e}")

with tab1:
    st.subheader("Register New Patient Profile")
    st.write("This form encrypts sensitive demographic parameters before database storage.")
    
    p_name = st.text_input("Full Name")
    p_dob = st.text_input("Date of Birth", placeholder="YYYY-MM-DD")
    p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    p_ssn = st.text_input("Social Security Number", placeholder="XXX-XX-XXXX")
    
    if st.button("Register Patient"):
        if not p_name or not p_dob or not p_ssn:
            st.warning("Please complete all fields.")
        else:
            try:
                payload = {
                    "name": p_name,
                    "dob": p_dob,
                    "gender": p_gender,
                    "ssn": p_ssn
                }
                res = requests.post(f"{BACKEND_URL}/records/patient", data=payload, headers=headers)
                if res.status_code == 200:
                    st.success(f"Registered patient: {p_name}")
                    st.rerun()
                else:
                    st.error(f"Failed to register patient: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Registration error: {e}")

with tab2:
    st.subheader("Upload Health Report")
    
    if not patients:
        st.info("No registered patients. Please create a patient profile first.")
    else:
        patient_options = {f"{pat['name']} (ID: {pat['id']})": pat["id"] for pat in patients}
        selected_patient = st.selectbox("Select Target Patient Profile", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient]
        
        uploaded_file = st.file_uploader("Choose Medical PDF", type=["pdf"])
        
        if uploaded_file:
            if st.button("🚀 Upload & Index"):
                with st.spinner("Uploading and encrypting..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        payload = {"patient_id": selected_patient_id}
                        
                        res = requests.post(f"{BACKEND_URL}/records/upload", files=files, data=payload, headers=headers)
                        if res.status_code == 200:
                            st.success(f"Uploaded record for {selected_patient}")
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.subheader("📋 Registered Patient Directory")
if not patients:
    st.info("No patient profiles registered yet.")
else:
    for pat in patients:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**Patient ID {pat['id']}**: `{pat['name']}` | DOB: `{pat['dob']}` | Gender: `{pat['gender']}`")
        with col2:
            # Check records for this patient
            try:
                rec_res = requests.get(f"{BACKEND_URL}/records?patient_id={pat['id']}", headers=headers)
                if rec_res.status_code == 200:
                    rec_list = rec_res.json()
                    st.markdown(f"Files uploaded: **{len(rec_list)}**")
            except Exception:
                pass
