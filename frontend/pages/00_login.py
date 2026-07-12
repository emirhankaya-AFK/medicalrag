import streamlit as st
import requests

BACKEND_URL = "http://localhost:8002"

st.set_page_config(page_title="Login - MedicalRAG", layout="wide")

st.title("🔑 User Authentication")

tab1, tab2 = st.tabs(["🔒 Sign In", "📝 Register New Account"])

with tab1:
    st.subheader("Login to your Session")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Sign In"):
        if not username or not password:
            st.warning("Please enter credentials.")
        else:
            try:
                # Login payload as form-data
                payload = {
                    "username": username,
                    "password": password
                }
                res = requests.post(f"{BACKEND_URL}/auth/token", data=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["username"] = data["username"]
                    st.session_state["role"] = data["role"]
                    st.success(f"Welcome back, {username}! Role: {data['role'].upper()}")
                    st.rerun()
                else:
                    st.error("Authentication failed. Check your username or password.")
            except Exception as e:
                st.error(f"Could not connect to auth service: {e}")

with tab2:
    st.subheader("Register a new user")
    reg_username = st.text_input("Choose Username", key="reg_username")
    reg_password = st.text_input("Choose Password", type="password", key="reg_password")
    reg_role = st.selectbox("Select Role", ["doctor", "nurse", "patient", "admin"], key="reg_role")
    
    if st.button("Register"):
        if not reg_username or not reg_password:
            st.warning("Please fill all details.")
        else:
            try:
                payload = {
                    "username": reg_username,
                    "password": reg_password,
                    "role": reg_role
                }
                res = requests.post(f"{BACKEND_URL}/auth/register", json=payload)
                if res.status_code == 200:
                    st.success("Registration complete! You can now sign in.")
                else:
                    st.error(f"Registration failed: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Error registering user: {e}")

# Session Action
st.markdown("<br><hr><br>", unsafe_allow_html=True)
if "token" in st.session_state and st.session_state["token"]:
    if st.button("🛑 Log Out"):
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.success("Session closed successfully.")
        st.rerun()
