import streamlit as st

def render_record_card(filename: str, upload_date: str, record_id: int):
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.8rem 1.2rem; border-radius: 8px; margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-weight: bold; color: #0F172A;">📋 {filename}</div>
            <div style="font-size: 0.8rem; color: #64748B;">Record ID: {record_id} | Uploaded: {upload_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
