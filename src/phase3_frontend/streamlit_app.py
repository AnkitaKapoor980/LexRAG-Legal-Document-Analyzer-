from __future__ import annotations

import streamlit as st
import pdfplumber
import requests
from typing import Optional

API_BASE = "http://localhost:8000"


def analyze_contract(contract_text: str, timeout: int = 600) -> dict:
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

    st.title("LexRAG — Contract Analyzer")
    st.markdown("Upload a contract PDF, run analysis, then ask questions about it.")

    # Main upload and analyze section
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

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        if st.button("Clear Analysis", use_container_width=True):
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("messages", None)
            st.rerun()
        
        st.markdown("---")
        
        with st.expander("🔧 Backend Diagnostics"):
            if st.button("Check Backend Health"):
                with st.spinner("Checking backend endpoints..."):
                    checks = []
                    # /health endpoint (GET)
                    try:
                        h = requests.get(f"{API_BASE}/health", timeout=5)
                        checks.append({
                            "endpoint": "/health",
                            "status": h.status_code,
                            "response": "✓ OK" if h.status_code == 200 else f"Error {h.status_code}"
                        })
                    except Exception as e:
                        checks.append({"endpoint": "/health", "error": str(e)})

                    # quick Q&A dry-run
                    try:
                        q = requests.post(f"{API_BASE}/api/qa", json={"question": "test", "clear_history": True}, timeout=10)
                        checks.append({
                            "endpoint": "/api/qa",
                            "status": q.status_code,
                            "response": "✓ OK" if q.status_code == 200 else f"Error {q.status_code}"
                        })
                    except Exception as e:
                        checks.append({"endpoint": "/api/qa", "error": str(e)})

                    for c in checks:
                        if "error" in c:
                            st.error(f"{c['endpoint']}: {c['error']}")
                        else:
                            st.success(f"{c['endpoint']}: {c['response']}")

    # Tabs for display
    tab_summary, tab_clauses, tab_risk, tab_compliance, tab_qa = st.tabs(
        ["Summary", "Clauses", "Risk Analysis", "Compliance", "Q&A Chat"]
    )

    analysis = st.session_state.get("analysis_result")

    with tab_summary:
        if analysis:
            summary_data = analysis.get("summary", {})
            
            # Main summary
            st.subheader("Contract Summary")
            summary_text = summary_data.get("summary", "No summary available")
            st.write(summary_text)
            
            st.markdown("---")
            
            # Key parties
            if summary_data.get("key_parties"):
                st.subheader("Key Parties")
                for party in summary_data.get("key_parties", []):
                    st.markdown(f"- {party}")
                st.markdown("")
            
            # Main obligations
            if summary_data.get("main_obligations"):
                st.subheader("Main Obligations")
                for obligation in summary_data.get("main_obligations", []):
                    st.markdown(f"- {obligation}")
                st.markdown("")
            
            # Key terms
            if summary_data.get("key_terms"):
                st.subheader("Key Terms")
                for term in summary_data.get("key_terms", []):
                    st.markdown(f"- {term}")
                st.markdown("")
            
            # Risk factors
            if summary_data.get("risk_factors"):
                st.subheader("Risk Factors")
                for risk in summary_data.get("risk_factors", []):
                    st.markdown(f"- {risk}")
                st.markdown("")
            
            # Important dates
            if summary_data.get("important_dates"):
                st.subheader("Important Dates")
                for date in summary_data.get("important_dates", []):
                    st.markdown(f"- {date}")
        else:
            st.info("No analysis yet. Upload a PDF and click 'Extract & Analyze'.")

    with tab_clauses:
        if analysis:
            clauses = analysis.get("clauses", [])
            
            # Group clauses by type
            grouped_clauses = {}
            for clause in clauses:
                clause_type = clause.get("clause_type", "other")
                if clause_type not in grouped_clauses:
                    grouped_clauses[clause_type] = []
                grouped_clauses[clause_type].append(clause)
            
            # Display grouped clauses
            st.subheader(f"Extracted Clauses ({len(clauses)} total)")
            st.markdown("Clauses are grouped by type for easier review.")
            st.markdown("---")
            
            for clause_type, clause_list in sorted(grouped_clauses.items()):
                # All collapsed by default - user clicks to expand
                with st.expander(f"{clause_type.title()} ({len(clause_list)} clauses)"):
                    for i, clause in enumerate(clause_list, 1):
                        st.markdown(f"**Clause {i}:**")
                        st.write(clause.get("clause_text", "No text available"))
                        
                        # Show risk and compliance if available
                        col1, col2 = st.columns(2)
                        with col1:
                            if "risk_analysis" in clause:
                                risk_level = clause["risk_analysis"].get("risk_level", "unknown")
                                risk_color = {"low": "green", "medium": "orange", "high": "red"}.get(risk_level, "gray")
                                st.markdown(f"::{risk_color}[Risk: {risk_level.upper()}]")
                        with col2:
                            if "compliance_check" in clause:
                                status = clause["compliance_check"].get("compliance_status", "unknown")
                                status_color = {"compliant": "green", "non-compliant": "red", "requires_review": "orange"}.get(status, "gray")
                                st.markdown(f"::{status_color}[Compliance: {status.replace('_', ' ').title()}]")
                        
                        if i < len(clause_list):
                            st.divider()
        else:
            st.info("No clauses: run analysis first.")

    with tab_risk:
        if analysis:
            st.subheader("Risk Analysis Overview")
            
            risk_dist = analysis.get("statistics", {}).get("risk_distribution", {})
            total_clauses = sum(risk_dist.values())
            
            if total_clauses > 0:
                st.markdown(f"**{total_clauses} clauses analyzed for risk**")
                st.markdown("---")
                
                # Risk distribution summary
                col1, col2, col3 = st.columns(3)
                
                high_count = risk_dist.get("high", 0)
                medium_count = risk_dist.get("medium", 0)
                low_count = risk_dist.get("low", 0)
                
                with col1:
                    st.metric("HIGH RISK", high_count, f"{(high_count/total_clauses*100):.0f}%")
                with col2:
                    st.metric("MEDIUM RISK", medium_count, f"{(medium_count/total_clauses*100):.0f}%")
                with col3:
                    st.metric("LOW RISK", low_count, f"{(low_count/total_clauses*100):.0f}%")
                
                st.markdown("---")
                
                # High risk clauses
                if high_count > 0:
                    st.subheader(f"HIGH RISK Clauses ({high_count})")
                    st.error("These clauses require immediate legal review")
                    
                    high_risk_clauses = [c for c in analysis.get("clauses", []) 
                                        if c.get("risk_analysis", {}).get("risk_level") == "high"]
                    
                    # Group by clause type
                    high_risk_grouped = {}
                    for clause in high_risk_clauses:
                        clause_type = clause.get("clause_type", "Unknown")
                        if clause_type not in high_risk_grouped:
                            high_risk_grouped[clause_type] = []
                        high_risk_grouped[clause_type].append(clause)
                    
                    # Display grouped - all collapsed by default
                    for clause_type, clauses_list in sorted(high_risk_grouped.items()):
                        with st.expander(f"{clause_type.title()} ({len(clauses_list)} clauses)"):
                            for i, clause in enumerate(clauses_list, 1):
                                st.write(f"**Clause {i}:**")
                                st.write(clause.get("clause_text", ""))
                                st.write("**Risk Explanation:**")
                                st.write(clause.get("risk_analysis", {}).get("explanation", "No explanation provided"))
                                if i < len(clauses_list):
                                    st.divider()
                    
                    st.markdown("---")
                
                # Medium risk clauses
                if medium_count > 0:
                    st.subheader(f"MEDIUM RISK Clauses ({medium_count})")
                    st.warning("These clauses should be reviewed")
                    
                    medium_risk_clauses = [c for c in analysis.get("clauses", []) 
                                          if c.get("risk_analysis", {}).get("risk_level") == "medium"]
                    
                    # Group by clause type
                    medium_risk_grouped = {}
                    for clause in medium_risk_clauses:
                        clause_type = clause.get("clause_type", "Unknown")
                        if clause_type not in medium_risk_grouped:
                            medium_risk_grouped[clause_type] = []
                        medium_risk_grouped[clause_type].append(clause)
                    
                    # Display grouped - all collapsed by default
                    for clause_type, clauses_list in sorted(medium_risk_grouped.items()):
                        with st.expander(f"{clause_type.title()} ({len(clauses_list)} clauses)"):
                            for i, clause in enumerate(clauses_list, 1):
                                st.write(f"**Clause {i}:**")
                                st.write(clause.get("clause_text", ""))
                                st.write("**Risk Explanation:**")
                                st.write(clause.get("risk_analysis", {}).get("explanation", "No explanation provided"))
                                if i < len(clauses_list):
                                    st.divider()
                    
                    st.markdown("---")
                
                # Low risk clauses
                if low_count > 0:
                    st.subheader(f"LOW RISK Clauses ({low_count})")
                    st.success("These clauses are generally acceptable")
                    
                    low_risk_clauses = [c for c in analysis.get("clauses", []) 
                                       if c.get("risk_analysis", {}).get("risk_level") == "low"]
                    
                    # Group by clause type
                    low_risk_grouped = {}
                    for clause in low_risk_clauses:
                        clause_type = clause.get("clause_type", "Unknown")
                        if clause_type not in low_risk_grouped:
                            low_risk_grouped[clause_type] = []
                        low_risk_grouped[clause_type].append(clause)
                    
                    # Display grouped - all collapsed by default
                    for clause_type, clauses_list in sorted(low_risk_grouped.items()):
                        with st.expander(f"{clause_type.title()} ({len(clauses_list)} clauses)"):
                            for i, clause in enumerate(clauses_list, 1):
                                st.write(f"**Clause {i}:**")
                                st.write(clause.get("clause_text", ""))
                                st.write("**Risk Explanation:**")
                                st.write(clause.get("risk_analysis", {}).get("explanation", "No explanation provided"))
                                if i < len(clauses_list):
                                    st.divider()
            else:
                st.info("No risk analysis data available")
        else:
            st.info("No risk info: run analysis first.")

    with tab_compliance:
        if analysis:
            st.subheader("Compliance Check Results")
            
            compliance_dist = analysis.get("statistics", {}).get("compliance_distribution", {})
            total_clauses = sum(compliance_dist.values())
            
            if total_clauses > 0:
                st.markdown(f"**{total_clauses} clauses checked for compliance with Indian law**")
                st.markdown("---")
                
                # Compliance distribution summary
                col1, col2, col3 = st.columns(3)
                
                compliant_count = compliance_dist.get("compliant", 0)
                non_compliant_count = compliance_dist.get("non-compliant", 0)
                review_count = compliance_dist.get("requires_review", 0)
                
                with col1:
                    st.metric("COMPLIANT", compliant_count, f"{(compliant_count/total_clauses*100):.0f}%")
                with col2:
                    st.metric("NON-COMPLIANT", non_compliant_count, f"{(non_compliant_count/total_clauses*100):.0f}%")
                with col3:
                    st.metric("REQUIRES REVIEW", review_count, f"{(review_count/total_clauses*100):.0f}%")
                
                st.markdown("---")
                
                # Non-compliant clauses (most important)
                if non_compliant_count > 0:
                    st.subheader(f"NON-COMPLIANT Clauses ({non_compliant_count})")
                    st.error("ATTENTION REQUIRED: These clauses may violate Indian law")
                    
                    non_compliant_clauses = [c for c in analysis.get("clauses", []) 
                                            if c.get("compliance_check", {}).get("compliance_status") == "non-compliant"]
                    
                    # Group by clause type
                    non_compliant_grouped = {}
                    for clause in non_compliant_clauses:
                        clause_type = clause.get("clause_type", "Unknown")
                        if clause_type not in non_compliant_grouped:
                            non_compliant_grouped[clause_type] = []
                        non_compliant_grouped[clause_type].append(clause)
                    
                    # Display grouped - all collapsed by default
                    for clause_type, clauses_list in sorted(non_compliant_grouped.items()):
                        with st.expander(f"{clause_type.title()} ({len(clauses_list)} clauses)"):
                            for i, clause in enumerate(clauses_list, 1):
                                st.write(f"**Clause {i}:**")
                                st.write(clause.get("clause_text", ""))
                                st.write("**Compliance Issue:**")
                                st.write(clause.get("compliance_check", {}).get("explanation", "No explanation provided"))
                                if i < len(clauses_list):
                                    st.divider()
                    
                    st.markdown("---")
                
                # Requires review
                if review_count > 0:
                    st.subheader(f"REQUIRES REVIEW Clauses ({review_count})")
                    st.warning("These clauses need additional legal review")
                    
                    review_clauses = [c for c in analysis.get("clauses", []) 
                                     if c.get("compliance_check", {}).get("compliance_status") == "requires_review"]
                    
                    # Group by clause type
                    review_grouped = {}
                    for clause in review_clauses:
                        clause_type = clause.get("clause_type", "Unknown")
                        if clause_type not in review_grouped:
                            review_grouped[clause_type] = []
                        review_grouped[clause_type].append(clause)
                    
                    # Display grouped - all collapsed by default
                    for clause_type, clauses_list in sorted(review_grouped.items()):
                        with st.expander(f"{clause_type.title()} ({len(clauses_list)} clauses)"):
                            for i, clause in enumerate(clauses_list, 1):
                                st.write(f"**Clause {i}:**")
                                st.write(clause.get("clause_text", ""))
                                st.write("**Review Notes:**")
                                st.write(clause.get("compliance_check", {}).get("explanation", "No explanation provided"))
                                if i < len(clauses_list):
                                    st.divider()
                    
                    st.markdown("---")
                
                # Compliant clauses (simplified view)
                if compliant_count > 0:
                    st.subheader(f"COMPLIANT Clauses ({compliant_count})")
                    st.success("These clauses comply with Indian law")
                    
                    compliant_clauses = [c for c in analysis.get("clauses", []) 
                                           if c.get("compliance_check", {}).get("compliance_status") == "compliant"]
                    
                    # Get unique clause types (deduplicate)
                    unique_types = sorted(set(c.get("clause_type", "Unknown") for c in compliant_clauses))
                    
                    with st.expander("View compliant clauses (by type)"):
                        for clause_type in unique_types:
                            st.markdown(f"- **{clause_type.title()}**")
            else:
                st.info("No compliance data available")
        else:
            st.info("No compliance info: run analysis first.")

    with tab_qa:
        st.subheader("Legal Q&A Assistant")
        st.markdown("Ask general questions about Indian law, legal concepts, or contract terms.")
        st.info("NOTE: This is a general legal assistant. For specific legal advice, consult a qualified lawyer.")
        
        # Initialize messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history in a container
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # Chat input at the bottom
        question = st.chat_input("Ask a legal question (e.g., 'What is a non-compete clause?', 'Should I sign this contract?')...")
        
        # Process new question
        if question:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Get AI response
            try:
                with st.spinner("Thinking..."):
                    result = ask_question(question)
                
                if result.get("ok"):
                    data = result.get("data", {})
                    answer = data.get("answer", "(no answer)")
                    notes = data.get("notes", "")
                    
                    # Add assistant message
                    if notes:
                        full_response = f"{answer}\n\n_{notes}_"
                    else:
                        full_response = answer
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    error_msg = f"Error: HTTP {result.get('status')}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"Request failed: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Rerun to display new messages
            st.rerun()


if __name__ == "__main__":
    main()
