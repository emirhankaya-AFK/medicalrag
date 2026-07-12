import streamlit as st
import requests
import pandas as pd
from ..components.auth_guard import check_auth

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Audit Logs - MedicalRAG", layout="wide")

# Restrict page strictly to admin roles
check_auth(allowed_roles=["admin"])

st.title("🛡️ Security Audit Logging Console")
st.write("HIPAA compliance access logs showing system modifications and query actions. All patient identifiers are masked in log details.")

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

if st.button("🔄 Refresh Logs"):
    st.rerun()

with st.spinner("Fetching system logs..."):
    try:
        res = requests.get(f"{BACKEND_URL}/audit/logs", headers=headers)
        if res.status_code == 200:
            logs = res.json()
            if not logs:
                st.info("No system activity logged yet.")
            else:
                # Convert logs list of dicts to pandas DataFrame for clean grid display
                df = pd.DataFrame(logs)
                # Reorder columns
                columns_order = ["id", "timestamp", "username", "user_role", "action", "accessed_resource", "details"]
                df = df[columns_order]
                
                # Format headers
                df.columns = ["Log ID", "Timestamp (UTC)", "User", "Role", "Action Type", "Resource Identifier", "Redacted Details"]
                
                # Render table
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("Failed to retrieve audit logs from backend security layer.")
    except Exception as e:
        st.error(f"Error connecting to audit service: {e}")
