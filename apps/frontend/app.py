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
    st.session_state.chat_history = []
    st.session_state.last_query = ""

if st.session_state.chat_history:
    with st.expander(f"Conversation History ({len(st.session_state.chat_history)})"):
        for h in st.session_state.chat_history:
            st.write(f"**Q:** {h['query']}")
            st.write(f"**A:** {h['answer']}")
            st.divider()

if st.session_state.stage == "input":
    query = st.text_input("Enter your research query:")
    st.session_state.last_query = query

    if st.button("Research"):
        if not query:
            st.warning("Please enter a query first.")
        else:
            with st.spinner("Researching and validating..."):
                ws = websocket.create_connection(WS_URL)
                ws.send(json.dumps({"query": query, "conversation_history": st.session_state.chat_history}))
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
        st.session_state.stage = "done"
        st.session_state.ws_connection = None
        st.session_state.last_result = final_message
        st.rerun()

elif st.session_state.stage == "done":
    final_message = st.session_state.last_result

    if final_message["status"] == "completed":
        st.success("Report ready!")
        st.write(final_message["report"])
        st.caption(f"Source: {final_message['source']}")

        col_a, col_b = st.columns(2)
        col_a.metric("Tokens Used", final_message.get("tokens", 0))
        col_b.metric("Estimated Cost", f"${final_message.get('cost', 0):.5f}")

        if final_message not in st.session_state.get("_saved_to_history", []):
            st.session_state.chat_history.append({
                "query": st.session_state.last_query,
                "answer": final_message.get("answer", "")
            })
            st.session_state.setdefault("_saved_to_history", []).append(final_message)
    else:
        st.warning(final_message.get("message", "Cancelled."))

    st.divider()
    if st.button("Ask Another Question"):
        st.session_state.stage = "input"
        st.rerun()