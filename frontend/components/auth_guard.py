import streamlit as st

def check_auth(allowed_roles=None):
    """
    Checks if a user is authenticated and has an allowed role.
    If not, halts execution with an error/redirect message.
    """
    if "token" not in st.session_state or not st.session_state["token"]:
        st.warning("🔒 Access Denied. Please log in first.")
        st.info("Navigate to the **00 login** page in the sidebar.")
        st.stop()
        
    if allowed_roles:
        role = st.session_state.get("role")
        if role not in allowed_roles:
            st.error(f"🚫 Forbidden. This page is restricted to roles: {allowed_roles}. Your role: {role}")
            st.stop()
