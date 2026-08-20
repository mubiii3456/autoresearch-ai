import streamlit as st
import requests

st.set_page_config(page_title="Cost Tracker", page_icon="💰")

st.title("Cost & Token Tracker")

BACKEND_URL = "http://127.0.0.1:8000"

response = requests.get(f"{BACKEND_URL}/reports")

if response.status_code == 200:
    report_list = response.json().get("reports", [])

    if not report_list:
        st.info("No reports yet. Run a query on the main page first.")
    else:
        total_tokens = 0
        total_cost = 0.0
        detailed_reports = []

        for r in report_list:
            detail_response = requests.get(f"{BACKEND_URL}/reports/{r['id']}")
            if detail_response.status_code == 200:
                detail = detail_response.json()
                tokens = detail.get("tokens", 0)
                cost = detail.get("cost", 0.0)
                total_tokens += tokens
                total_cost += cost
                detailed_reports.append({
                    "Query": detail.get("query"),
                    "Tokens": tokens,
                    "Cost ($)": round(cost, 5),
                    "Date": detail.get("created_at", "")[:10]
                })

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Queries", len(report_list))
        col2.metric("Total Tokens Used", total_tokens)
        col3.metric("Total Estimated Cost", f"${total_cost:.5f}")

        st.divider()
        st.subheader("Breakdown by Query")
        st.dataframe(detailed_reports, use_container_width=True)
else:
    st.error("Could not fetch reports.")