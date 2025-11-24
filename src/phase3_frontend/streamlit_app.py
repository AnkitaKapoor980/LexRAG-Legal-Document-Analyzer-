from __future__ import annotations

import streamlit as st
import pdfplumber
import requests
from typing import Optional

API_BASE = "http://localhost:8000"


def analyze_contract(contract_text: str, timeout: int = 300) -> dict:
    resp = requests.post(
        f"{API_BASE}/api/analyze-document",
        json={
            "contract_text": contract_text,
            "extract_clauses": True,
            "analyze_risks": True,
            "check_compliance": True,
            "generate_summary": True,
        },
        timeout=timeout,
    )
    try:
        resp.raise_for_status()
        return {"ok": True, "status": resp.status_code, "data": resp.json(), "text": resp.text}
    except requests.HTTPError:
        # return raw body so the UI can show server error messages
        return {"ok": False, "status": resp.status_code, "text": resp.text}


def ask_question(question: str, clear_history: bool = False) -> dict:
    resp = requests.post(f"{API_BASE}/api/qa", json={"question": question, "clear_history": clear_history})
    try:
        resp.raise_for_status()
        return {"ok": True, "status": resp.status_code, "data": resp.json(), "text": resp.text}
    except requests.HTTPError:
        return {"ok": False, "status": resp.status_code, "text": resp.text}


def extract_text_from_pdf(uploaded_file) -> str:
    with pdfplumber.open(uploaded_file) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n\n".join(pages)


def main() -> None:
    st.set_page_config(page_title="LexRAG — Contract Analyzer", layout="wide")

    st.title("LexRAG — Contract Analyzer (Phase 3)")
    st.markdown("Upload a contract PDF, run analysis, then ask questions about it.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])
        if uploaded_file:
            if st.button("Extract & Analyze"):
                with st.spinner("Extracting text from PDF..."):
                    contract_text = extract_text_from_pdf(uploaded_file)
                with st.spinner("Sending to backend for analysis (this may take a while)..."):
                    try:
                        analysis_result = analyze_contract(contract_text)
                        if analysis_result.get("ok"):
                            # normalize stored analysis to be the actual data object
                            st.session_state.analysis_result = analysis_result.get("data", {})
                            st.success("Analysis complete")
                        else:
                            st.error(f"Analysis failed: HTTP {analysis_result.get('status')}")
                            with st.expander("Server response body"):
                                st.text(analysis_result.get("text", "(no body)"))
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    with col2:
        st.header("Controls")
        if st.button("Check Backend"):
            with st.spinner("Checking backend endpoints..."):
                checks = []
                # /health endpoint (GET)
                try:
                    h = requests.get(f"{API_BASE}/health", timeout=5)
                    try:
                        body = h.json()
                    except Exception:
                        body = h.text
                    checks.append({"endpoint": "/health", "status": h.status_code, "body": body})
                except Exception as e:
                    checks.append({"endpoint": "/health", "error": str(e)})

                # quick Q&A dry-run
                try:
                    q = requests.post(f"{API_BASE}/api/qa", json={"question": "health check", "clear_history": True}, timeout=10)
                    try:
                        qbody = q.json()
                    except Exception:
                        qbody = q.text
                    checks.append({"endpoint": "/api/qa", "status": q.status_code, "body": qbody})
                except Exception as e:
                    checks.append({"endpoint": "/api/qa", "error": str(e)})

                st.subheader("Backend diagnostics")
                for c in checks:
                    st.write(c)
        if st.button("Clear Analysis"):
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("messages", None)

    # Tabs for display
    tab_summary, tab_clauses, tab_risk, tab_compliance, tab_qa = st.tabs(
        ["Summary", "Clauses", "Risk Analysis", "Compliance", "Q&A Chat"]
    )

    analysis = st.session_state.get("analysis_result")

    with tab_summary:
        if analysis:
            st.subheader("Summary")
            st.write(analysis.get("summary", {}))
        else:
            st.info("No analysis yet. Upload a PDF and click 'Extract & Analyze'.")

    with tab_clauses:
        if analysis:
            for clause in analysis.get("clauses", []):
                st.markdown(f"**{clause.get('clause_type','Clause').title()}**")
                st.write(clause.get("clause_text"))
                st.divider()
        else:
            st.info("No clauses: run analysis first.")

    with tab_risk:
        if analysis:
            st.subheader("Risk distribution")
            st.write(analysis.get("statistics", {}).get("risk_distribution", {}))
        else:
            st.info("No risk info: run analysis first.")

    with tab_compliance:
        if analysis:
            st.subheader("Compliance overview")
            st.write(analysis.get("statistics", {}).get("compliance_distribution", {}))
        else:
            st.info("No compliance info: run analysis first.")

    with tab_qa:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("Ask a question about the contract...")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            try:
                result = ask_question(question)
                if result.get("ok"):
                    data = result.get("data", {})
                    answer = data.get("answer", "(no answer)")
                    sources = data.get("sources", [])
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    with st.chat_message("assistant"):
                        st.write(answer)
                        if sources:
                            with st.expander("Sources"):
                                for s in sources:
                                    st.write(s)
                    # raw JSON view
                    with st.expander("Raw JSON response"):
                        st.json(data)
                else:
                    # server returned non-2xx; show body for debugging
                    st.error(f"Q&A failed: HTTP {result.get('status')} - see server message below")
                    with st.expander("Server response body"):
                        st.text(result.get("text", "(no body)"))
            except Exception as e:
                st.error(f"Q&A request failed locally: {e}")


if __name__ == "__main__":
    main()
