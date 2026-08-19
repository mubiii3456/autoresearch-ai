import streamlit as st
import requests

st.set_page_config(page_title="AutoResearch AI", page_icon="🔍")

st.title("AutoResearch AI")
st.write("Ask a question and get a researched, fact-checked report.")

BACKEND_URL = "http://127.0.0.1:8000/research"

query = st.text_input("Enter your research query:")

if st.button("Research"):
    if not query:
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Researching... this may take a moment."):
            response = requests.post(BACKEND_URL, json={"query": query})

        if response.status_code == 200:
            data = response.json()

            if data["status"] == "needs_clarification":
                st.info(f"Clarification needed: {data['question']}")
            else:
                st.success("Report ready!")
                st.write(data["report"])
                st.caption(f"Source: {data['source']}")
        else:
            st.error("Something went wrong. Please try again.")