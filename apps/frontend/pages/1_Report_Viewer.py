import os 
import streamlit as st
import requests
from theme import inject_theme

st.set_page_config(page_title="Report Viewer", page_icon="📄")

inject_theme()

st.title("Saved Reports")

BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
BACKEND_URL = f"http://{BACKEND_HOST}:8000"

response = requests.get(f"{BACKEND_URL}/reports")

if response.status_code == 200:
    reports = response.json().get("reports", [])

    if not reports:
        st.info("No reports saved yet. Go run a query on the main page first.")
    else:
        for r in reports:
            with st.expander(f"{r['query']} — {r['created_at'][:10]}"):
                detail_response = requests.get(f"{BACKEND_URL}/reports/{r['id']}")
                if detail_response.status_code == 200:
                    detail = detail_response.json()
                    st.write(f"**Claim:** {detail.get('claim')}")
                    st.write(f"**Source:** {detail.get('source')}")
                    st.caption(f"Report ID: {detail.get('id')}")
else:
    st.error("Could not fetch reports.")