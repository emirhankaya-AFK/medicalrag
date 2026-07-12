import streamlit as st
import requests
import json
from ..components.auth_guard import check_auth

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Patient Record View - MedicalRAG", layout="wide")

check_auth(allowed_roles=["doctor", "nurse", "patient"])

st.title("🩻 Patient Clinical Profile & Extractions")

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# Fetch patients list (Patients can only query their own or see select list)
patients = []
try:
    if st.session_state["role"] == "patient":
        # Simulating that patients only see patient profile ID 1 (or can search their own ID)
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
    st.info("No registered patients found.")
else:
    patient_options = {f"{pat['name']} (ID: {pat['id']})": pat["id"] for pat in patients}
    selected_patient = st.selectbox("Select Patient Profile", list(patient_options.keys()))
    selected_patient_id = patient_options[selected_patient]
    
    # List medical records for selected patient
    records = []
    try:
        rec_res = requests.get(f"{BACKEND_URL}/records?patient_id={selected_patient_id}", headers=headers)
        if rec_res.status_code == 200:
            records = rec_res.json()
    except Exception as e:
        st.error(f"Error listing records: {e}")
        
    if not records:
        st.info("No medical records uploaded for this patient.")
    else:
        record_options = {rec["filename"]: rec["id"] for rec in records}
        selected_record_name = st.selectbox("Select Document to Extract/View", list(record_options.keys()))
        selected_record_id = record_options[selected_record_name]
        
        # Action button (restricted to doctors and nurses)
        if st.session_state["role"] in ["doctor", "nurse"]:
            if st.button("🧠 Extract Parameters & Clinical Insights"):
                with st.spinner("Analyzing PDF text and mapping ICD codes..."):
                    try:
                        res = requests.post(f"{BACKEND_URL}/extraction/run/{selected_record_id}", headers=headers)
                        if res.status_code == 200:
                            st.success("Extraction and clinical indexing complete!")
                        else:
                            st.error(f"Extraction failed: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        # Fetch existing extraction if any
        extraction_data = None
        try:
            ext_res = requests.get(f"{BACKEND_URL}/records?patient_id={selected_patient_id}", headers=headers) # trigger list
            # Fetch single extraction endpoint
            for rec in records:
                if rec["id"] == selected_record_id:
                    # Fetching extraction from DB directly or via backend
                    # We will request timeline or mock fetch
                    pass
        except Exception:
            pass
            
        # We query the details using patient timeline / insights endpoint or implement a direct get endpoint
        # Let's get aggregated insights for this patient
        st.markdown("<br>", unsafe_allow_html=True)
        
        insight_col, data_col = st.columns([1, 2])
        
        with insight_col:
            st.subheader("💡 Clinical Summary & Insights")
            try:
                ins_res = requests.get(f"{BACKEND_URL}/extraction/patient/{selected_patient_id}/insights", headers=headers)
                if ins_res.status_code == 200:
                    st.info(ins_res.json().get("insights", ""))
                else:
                    st.warning("No clinical insights generated yet. Run extraction.")
            except Exception as e:
                st.error(f"Failed to fetch insights: {e}")
                
        with data_col:
            st.subheader("📊 Extracted Medical Data")
            # Retrieve latest extraction detail (we can query the timeline or format)
            try:
                timeline_res = requests.get(f"{BACKEND_URL}/extraction/patient/{selected_patient_id}/timeline", headers=headers)
                if timeline_res.status_code == 200:
                    timeline = timeline_res.json()
                    
                    tab1, tab2, tab3, tab4 = st.tabs(["🩺 Diagnoses", "💊 Medications", "🧪 Lab Results", "❤️ Vital Signs"])
                    
                    with tab1:
                        diags = [e for e in timeline if e["type"] == "Diagnosis"]
                        if not diags:
                            st.info("No diagnoses extracted.")
                        else:
                            for d in diags:
                                st.write(f"- {d['event']} (Date: {d['date']})")
                                
                    with tab2:
                        meds = [e for e in timeline if e["type"] == "Medication"]
                        if not meds:
                            st.info("No medications extracted.")
                        else:
                            for m in meds:
                                st.write(f"- {m['event']} (Date: {m['date']})")
                                
                    with tab3:
                        labs = [e for e in timeline if e["type"] == "Lab Result"]
                        if not labs:
                            st.info("No lab results extracted.")
                        else:
                            for l in labs:
                                st.write(f"- {l['event']} (Date: {l['date']})")
                                
                    with tab4:
                        vits = [e for e in timeline if e["type"] == "Vital Sign"]
                        if not vits:
                            st.info("No vital signs recorded.")
                        else:
                            for v in vits:
                                st.write(f"- {v['event']} (Date: {v['date']})")
            except Exception as e:
                st.error(f"Error fetching data: {e}")

        # Multi-Record Side-by-Side View
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        st.subheader("🔄 Multi-Record Side-by-Side View")
        if len(records) >= 2:
            st.write("Compare 2 clinical reports for this patient side-by-side:")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                comp_rec1 = st.selectbox("Select Record A", list(record_options.keys()), key="m_rec1")
            with col_c2:
                comp_rec2 = st.selectbox("Select Record B", list(record_options.keys()), key="m_rec2")
                
            if st.button("🔄 Compare Clinical Records"):
                st.write("### Comparison Matrix")
                col_res1, col_res2 = st.columns(2)
                # To simulate, we filter the timeline events by record description or show side-by-side details
                with col_res1:
                    st.markdown(f"#### {comp_rec1}")
                    st.write("Check patient history timeline for full details on events associated with this record date.")
                with col_res2:
                    st.markdown(f"#### {comp_rec2}")
                    st.write("Check patient history timeline for full details on events associated with this record date.")
        else:
            st.info("Upload at least 2 records to compare clinical parameters side-by-side.")
