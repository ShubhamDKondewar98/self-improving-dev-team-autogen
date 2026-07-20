import asyncio
import streamlit as st
from orchestration.run_manager import run_dev_team
from orchestration.attempt_logger import log_attempt, list_attempts, load_attempt , update_attempt_decision

st.set_page_config(page_title="Self-Improving Dev Team", layout="wide")
st.title("Self-Improving Agentic Dev Team")

tab_run, tab_history = st.tabs(["Run a Task", "History"])

with tab_run:
    task = st.text_area("Task description", placeholder="Write a function that...")

    if st.button("Run", type="primary", disabled=not task.strip()):
        with st.spinner("Running dev team loop..."):
            result = asyncio.run(run_dev_team(task))
            st.session_state["last_result"] = result
            st.session_state["last_logpath"] = log_attempt(result)

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]

        st.divider()
        st.subheader("Result")

        col1, col2, col3 = st.columns(3)
        col1.metric("Verdict", result["final_verdict"])
        col2.metric("Code retries", result["code_retry_count"])
        col3.metric("Test retries", result["test_retry_count"])

        st.caption(f"Stop reason: {result['stop_reason']}")

        if result["failure_category"]:
            st.warning(f"Failure category: {result['failure_category']}")

        st.subheader("Final Code")
        st.code(result["final_code"] or "No code produced.", language="python")

        st.subheader("Critic Reasoning")
        st.write(result["critic_reasoning"] or "No reasoning captured.")

        st.subheader("Full Conversation Trace")
        for m in result["messages"]:
            with st.expander(f"{m['source']}"):
                st.text(m["content"])

        st.divider()
        st.subheader("Human Decision")
        c1, c2 = st.columns(2)
        if c1.button("Approve", type="primary"):
            update_attempt_decision(st.session_state["last_logpath"], "APPROVED")
            st.success("Approved and saved to log.")
        if c2.button("Reject"):
            update_attempt_decision(st.session_state["last_logpath"], "REJECTED")
            st.error("Rejected and saved to log.")  


with tab_history:
    st.subheader("Past Runs")
    attempts = list_attempts()
    if not attempts:
        st.info("No runs logged yet.") 

   

    for filepath in attempts:
        data = load_attempt(filepath)
        if data is None:
            continue
        with st.expander(f"{data.get('timestamp')} — {data.get('final_verdict')} — {data.get('task', '')[:60]}"):
            st.json(data)