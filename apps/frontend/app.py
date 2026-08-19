import streamlit as st
import websocket
import json

st.set_page_config(page_title="AutoResearch AI", page_icon="🔍")

st.title("AutoResearch AI")
st.write("Ask a question and get a researched, fact-checked report.")

WS_URL = "ws://127.0.0.1:8000/ws/research"

if "stage" not in st.session_state:
    st.session_state.stage = "input"
    st.session_state.pending_claim = None
    st.session_state.pending_source = None
    st.session_state.ws_connection = None

if st.session_state.stage == "input":
    query = st.text_input("Enter your research query:")

    if st.button("Research"):
        if not query:
            st.warning("Please enter a query first.")
        else:
            with st.spinner("Researching and validating..."):
                ws = websocket.create_connection(WS_URL)
                ws.send(json.dumps({"query": query}))
                message = json.loads(ws.recv())

            if message["type"] == "approval_needed":
                st.session_state.stage = "approval"
                st.session_state.pending_claim = message["claim"]
                st.session_state.pending_source = message["source"]
                st.session_state.ws_connection = ws
                st.rerun()

            elif message["type"] == "final":
                ws.close()
                if message["status"] == "needs_clarification":
                    st.info(f"Clarification needed: {message['question']}")
                elif message["status"] == "max_retries":
                    st.error(message["message"])

elif st.session_state.stage == "approval":
    st.subheader("Review Before Finalizing")
    st.write(f"**Claim:** {st.session_state.pending_claim}")
    st.write(f"**Source:** {st.session_state.pending_source}")

    col1, col2 = st.columns(2)
    approve_clicked = col1.button("✅ Approve and Generate Report")
    reject_clicked = col2.button("❌ Reject")

    if approve_clicked or reject_clicked:
        ws = st.session_state.ws_connection

        with st.spinner("Generating final report..."):
            ws.send(json.dumps({"approved": approve_clicked}))
            final_message = json.loads(ws.recv())

        ws.close()
        st.session_state.stage = "input"
        st.session_state.ws_connection = None

        if final_message["status"] == "completed":
            st.success("Report ready!")
            st.write(final_message["report"])
            st.caption(f"Source: {final_message['source']}")

            col_a, col_b = st.columns(2)
            col_a.metric("Tokens Used", final_message.get("tokens", 0))
            col_b.metric("Estimated Cost", f"${final_message.get('cost', 0):.5f}")
        else:
            st.warning(final_message.get("message", "Cancelled."))