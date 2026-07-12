import streamlit as st

st.set_page_config(
    page_title="MedicalRAG - Clinical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Home page design
st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0F766E;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .user-badge {
        background-color: #F0FDFA;
        border: 1px solid #CCFBF1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: #0D9488;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🩺 MedicalRAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Secure, HIPAA-Conscious Medical Records Q&A and Clinical Timeline System</div>', unsafe_allow_html=True)

# Login Status Check
if "token" in st.session_state and st.session_state["token"]:
    st.markdown(f'<div class="user-badge">🔓 Logged in as: {st.session_state["username"]} ({st.session_state["role"].upper()})</div>', unsafe_allow_html=True)
else:
    st.warning("🔒 You are not logged in. Please navigate to 00_login page in the sidebar.")

st.write(
    "MedicalRAG assists healthcare professionals and patients by parsing medical records, "
    "structuring vital data, generating chronological patient timelines, and "
    "answering medical questions with safety guardrails."
)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔒 Security & HIPAA Features")
    st.markdown("""
    - **PII Encryption**: AES-256 encryption on patient names, dates of birth, and SSNs at rest in the database.
    - **Role-Based Access Control (RBAC)**: Segregated views for Doctors, Nurses, and Patients.
    - **Audit Trails**: Full system logs recording who accessed what data, when, with PII redaction.
    - **Rate Limiting**: Automatic safety mechanism preventing scraping or high-volume queries.
    """)

with col2:
    st.subheader("💡 Clinical Assistant Capabilities")
    st.markdown("""
    - **Structured Extractions**: Extract ICD-10 diagnoses, dosages, lab reference bounds, and vitals.
    - **OCR fallback**: Parse scanned health records and prescription slips.
    - **Aggregated Timelines**: Chronological patient timeline aggregating labs, meds, and diagnoses.
    - **Clinical Guardrails**: Safety filters preventing AI diagnostic advice and patient HIPAA leaks.
    """)
