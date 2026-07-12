import streamlit as st
import requests
from ..components.auth_guard import check_auth

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Medical Q&A - MedicalRAG", layout="wide")

check_auth(allowed_roles=["doctor", "nurse", "patient"])

st.title("💬 Secure Clinical Q&A")
st.write("Query the indexed patient history. Safety guardrails block unauthorized diagnostic generation or HIPAA leaks.")

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# Fetch patients list
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
    
    question = st.text_input("Enter clinical question:", placeholder="e.g., What medications is this patient taking? List vital signs.")
    
    # HIPAA consent checkbox for patients
    consent = True
    if st.session_state["role"] == "patient":
        consent = st.checkbox("I authorize MedicalRAG to display my medical records contents in this chat session.")

    if st.button("🩺 Query Assistant"):
        if not question.strip():
            st.warning("Please enter a question.")
        elif not consent:
            st.error("You must authorize access to display record information.")
        else:
            with st.spinner("Processing query under HIPAA compliance guidelines..."):
                try:
                    payload = {
                        "patient_id": selected_patient_id,
                        "question": question
                    }
                    res = requests.post(f"{BACKEND_URL}/qa", json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        st.write("### Response")
                        if data.get("blocked", False):
                            st.warning(data["answer"])
                        else:
                            st.info(data["answer"])
                            
                            st.write("### Sources Citations")
                            citations = data.get("citations", [])
                            if not citations:
                                st.write("No specific section cited.")
                            else:
                                for cit in citations:
                                    st.markdown(f"""
                                    <div style="background-color: #F0FDF4; border: 1px solid #DCFCE7; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem;">
                                        <div style="font-weight: bold; color: #166534; font-size: 0.85rem; margin-bottom: 0.2rem;">
                                            Source #{cit['source_index']}
                                        </div>
                                        <div style="font-style: italic; color: #14532D; font-size: 0.9rem;">
                                            "{cit['snippet']}"
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.error(f"Failed to query assistant: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection error to backend: {e}")
