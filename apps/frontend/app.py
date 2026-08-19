import streamlit as st
import websocket
import json

st.set_page_config(page_title="AutoResearch AI", page_icon="🔍")

st.title("AutoResearch AI")
st.write("Ask a question and get a researched, fact-checked report.")

WS_URL = "ws://127.0.0.1:8000/ws/research"

query = st.text_input("Enter your research query:")

if st.button("Research"):
    if not query:
        st.warning("Please enter a query first.")
    else:
        status_placeholder = st.empty()
        steps_log = []

        ws = websocket.create_connection(WS_URL)
        ws.send(json.dumps({"query": query}))

        final_data = None

        while True:
            message = json.loads(ws.recv())

            if message["type"] == "step":
                steps_log.append(message["message"])
                status_placeholder.info("\n\n".join(steps_log))
            elif message["type"] == "final":
                final_data = message
                break

        ws.close()

        if final_data["status"] == "needs_clarification":
            st.info(f"Clarification needed: {final_data['question']}")
        else:
            st.success("Report ready!")
            st.write(final_data["report"])
            st.caption(f"Source: {final_data['source']}")