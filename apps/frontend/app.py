import os
import streamlit as st
import websocket
import json
from theme import inject_theme, render_pipeline

st.set_page_config(page_title="AutoResearch AI", page_icon="🔍")

inject_theme()

st.title("AutoResearch AI")
st.write("Ask a question and get a researched, fact-checked report.")

render_pipeline()

BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1")
WS_URL = f"ws://{BACKEND_HOST}:8000/ws/research"
BACKEND_URL = f"http://{BACKEND_HOST}:8000"

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
    st.markdown(f"""
        <div class="approval-card">
            <p style="color:#E8A33D; font-family:'JetBrains Mono', monospace; font-size:0.75rem; margin-bottom:8px;">
                REVIEW BEFORE FINALIZING
            </p>
            <p style="margin-bottom:6px;"><strong>Claim:</strong> {st.session_state.pending_claim}</p>
            <p style="color:#8792A6; font-size:0.85rem;"><strong>Source:</strong> {st.session_state.pending_source}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
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
        st.markdown(f"""
            <div class="report-card">
                <p style="color:#4FD1C5; font-family:'JetBrains Mono', monospace; font-size:0.75rem; margin-bottom:10px;">
                    ✓ REPORT READY
                </p>
                <p style="line-height:1.6;">{final_message['report']}</p>
                <p style="color:#8792A6; font-size:0.8rem; margin-top:14px;">Source: {final_message['source']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
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