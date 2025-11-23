# Phase 3 Frontend Integration Guide

## 🎯 Overview

Phase 3 needs to build a **Streamlit web application** that allows users to:
1. **Upload PDF contracts** for analysis
2. **View analysis results** (clauses, risks, compliance, summary)
3. **Ask questions** about the contract via chat interface
4. **See citations** and legal references

This document explains exactly how to integrate with Phase 2 backend.

---

## 🔌 Backend API Integration

### Starting the Backend

**First, start the Phase 2 API server:**

```powershell
# From project root
python scripts/run_phase2_api.py
```

**Or directly:**
```powershell
uvicorn src.phase2_agents.api.main:app --reload --port 8000
```

**Verify it's running:**
- Visit: http://localhost:8000/docs
- You should see Swagger UI with all API endpoints

---

## 📡 API Endpoints to Use

### 1. Full Document Analysis (Main Endpoint)

**Endpoint**: `POST /api/analyze-document`

**Use Case**: When user uploads a PDF contract

**Request**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze-document",
    json={
        "contract_text": "Full contract text extracted from PDF...",
        "extract_clauses": True,
        "analyze_risks": True,
        "check_compliance": True,
        "generate_summary": True
    }
)

result = response.json()
```

**Response Structure**:
```json
{
  "document_length": 4323,
  "clauses": [
    {
      "clause_type": "termination",
      "clause_text": "Either party may terminate...",
      "start_position": 245,
      "importance": "high",
      "risk_analysis": {
        "risk_level": "low",
        "explanation": "Clear notice periods...",
        "concerns": []
      },
      "compliance_check": {
        "compliance_status": "compliant",
        "violations": [],
        "relevant_acts": ["Indian Contract Act, 1872"],
        "citations": [...]
      }
    }
  ],
  "summary": {
    "summary": "Contract summary text...",
    "key_parties": ["Party A", "Party B"],
    "main_obligations": ["Obligation 1", "Obligation 2"],
    "key_terms": ["Term 1", "Term 2"],
    "risk_factors": ["Risk 1"],
    "important_dates": ["Date 1"]
  },
  "statistics": {
    "total_clauses": 26,
    "risk_distribution": {"low": 18, "medium": 7, "high": 1},
    "compliance_distribution": {"compliant": 15, "requires_review": 11}
  }
}
```

---

### 2. Q&A Chat Endpoint

**Endpoint**: `POST /api/qa`

**Use Case**: User asks questions about the contract

**Request**:
```python
response = requests.post(
    "http://localhost:8000/api/qa",
    json={
        "question": "What is the termination clause?",
        "clear_history": False  # Set True to start new conversation
    }
)

result = response.json()
```

**Response Structure**:
```json
{
  "answer": "The termination clause states that...",
  "sources": [
    {
      "chunk_id": "contract_1_chunk_001",
      "title": "Contract Title",
      "source": "path/to/document",
      "year": "2024",
      "similarity_score": 0.85
    }
  ],
  "confidence": "high",
  "notes": "Based on contract analysis..."
}
```

**Important**: 
- Don't set `clear_history=True` for follow-up questions
- Each question builds on conversation context
- Use `clear_history=True` when user uploads a new document

---

### 3. Individual Agent Endpoints (Optional)

You can also call individual agents:

- `POST /api/extract-clauses` - Extract clauses only
- `POST /api/analyze-risk` - Analyze risk of single clause
- `POST /api/check-compliance` - Check compliance of single clause
- `POST /api/summarize` - Generate summary only

**But**: Use `/api/analyze-document` for full analysis - it's more efficient!

---

## 📋 Frontend Workflow

### Complete User Flow

```
1. User opens Streamlit app
   ↓
2. User uploads PDF contract
   ↓
3. Frontend extracts text from PDF (use PyPDF2/pdfplumber)
   ↓
4. Frontend calls POST /api/analyze-document
   ↓
5. Backend processes (may take 30 seconds - 4 minutes)
   ↓
6. Frontend displays results:
   - Extracted Clauses tab
   - Risk Analysis tab (color-coded)
   - Compliance Check tab
   - Summary tab
   ↓
7. User asks questions in chat
   ↓
8. Frontend calls POST /api/qa for each question
   ↓
9. Frontend displays answer with citations
```

---

## 🛠️ Implementation Steps

### Step 1: PDF Text Extraction

**Add to requirements.txt** (if not already there):
```
PyPDF2>=3.0.1
pdfplumber>=0.11.0
streamlit>=1.28.0
requests>=2.32.0
```

**Extract text from PDF**:
```python
import pdfplumber
import streamlit as st

uploaded_file = st.file_uploader("Upload Contract PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        contract_text = "\n".join([page.extract_text() for page in pdf.pages])
```

---

### Step 2: Call Backend API

**Create API client function**:
```python
import requests

API_BASE_URL = "http://localhost:8000"

def analyze_contract(contract_text: str):
    """Call backend to analyze contract."""
    response = requests.post(
        f"{API_BASE_URL}/api/analyze-document",
        json={
            "contract_text": contract_text,
            "extract_clauses": True,
            "analyze_risks": True,
            "check_compliance": True,
            "generate_summary": True
        },
        timeout=300  # 5 minutes timeout for large contracts
    )
    response.raise_for_status()
    return response.json()

def ask_question(question: str, clear_history: bool = False):
    """Ask question about contract."""
    response = requests.post(
        f"{API_BASE_URL}/api/qa",
        json={
            "question": question,
            "clear_history": clear_history
        }
    )
    response.raise_for_status()
    return response.json()
```

---

### Step 3: Display Results in Streamlit

**Tabs structure**:
```python
import streamlit as st

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Summary", 
    "Clauses", 
    "Risk Analysis", 
    "Compliance", 
    "Q&A Chat"
])

# Tab 1: Summary
with tab1:
    if analysis_result:
        summary = analysis_result["summary"]
        st.header("Contract Summary")
        st.write(summary["summary"])
        st.subheader("Key Parties")
        st.write(summary["key_parties"])
        # ... more summary fields

# Tab 2: Clauses
with tab2:
    clauses = analysis_result["clauses"]
    for clause in clauses:
        st.subheader(f"{clause['clause_type'].title()} Clause")
        st.write(clause["clause_text"])
        # ... more clause details

# Tab 3: Risk Analysis (with color coding)
with tab3:
    for clause in clauses:
        risk_level = clause["risk_analysis"]["risk_level"]
        if risk_level == "high":
            st.error(f"🔴 High Risk: {clause['clause_type']}")
        elif risk_level == "medium":
            st.warning(f"🟡 Medium Risk: {clause['clause_type']}")
        else:
            st.success(f"🟢 Low Risk: {clause['clause_type']}")

# Tab 4: Compliance
with tab4:
    for clause in clauses:
        compliance = clause["compliance_check"]
        status = compliance["compliance_status"]
        if status == "compliant":
            st.success(f"✅ {clause['clause_type']}: Compliant")
        elif status == "non-compliant":
            st.error(f"❌ {clause['clause_type']}: Non-Compliant")
        else:
            st.info(f"⚠️ {clause['clause_type']}: Requires Review")

# Tab 5: Q&A Chat
with tab5:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    question = st.chat_input("Ask a question about the contract...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        
        # Call API
        answer_result = ask_question(question)
        
        with st.chat_message("assistant"):
            st.write(answer_result["answer"])
            if answer_result["sources"]:
                with st.expander("Sources"):
                    for source in answer_result["sources"]:
                        st.write(f"- {source['title']}")
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer_result["answer"]
        })
```

---

## 🎨 UI/UX Recommendations

### 1. Loading States

Show progress during analysis:
```python
with st.spinner("Analyzing contract... This may take 1-4 minutes"):
    result = analyze_contract(contract_text)
```

### 2. Error Handling

```python
try:
    result = analyze_contract(contract_text)
except requests.exceptions.Timeout:
    st.error("Analysis timed out. Please try with a shorter contract.")
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to backend. Make sure API server is running on port 8000.")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

### 3. Color Coding

- **Risk Levels**: 
  - 🔴 Red for High Risk
  - 🟡 Yellow for Medium Risk
  - 🟢 Green for Low Risk

- **Compliance**:
  - ✅ Green for Compliant
  - ❌ Red for Non-Compliant
  - ⚠️ Yellow for Requires Review

### 4. Citations Display

Show clickable citations:
```python
with st.expander("View Citations"):
    for citation in sources:
        st.markdown(f"[{citation['title']}]({citation.get('source_url', '#')})")
        st.caption(f"Similarity: {citation['similarity_score']:.2f}")
```

---

## 📦 Required Setup for Phase 3

### 1. Environment Variables

Create `.env` file (already exists):
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### 2. Dependencies

Add to `requirements.txt`:
```
streamlit>=1.28.0
requests>=2.32.0
PyPDF2>=3.0.1
pdfplumber>=0.11.0
```

### 3. Backend Running

**Always start backend first:**
```powershell
python scripts/run_phase2_api.py
```

---

## 🔄 Session Management

### For Multiple Contracts

When user uploads a new contract:
1. Clear Q&A chat history: `clear_history=True`
2. Clear previous analysis results
3. Show new analysis

**Implementation**:
```python
if uploaded_file:
    # Clear previous session
    if "analysis_result" in st.session_state:
        del st.session_state.analysis_result
    if "messages" in st.session_state:
        st.session_state.messages = []
    
    # Process new contract
    contract_text = extract_text(uploaded_file)
    st.session_state.analysis_result = analyze_contract(contract_text)
```

---

## 📊 Example Response Handling

### Displaying Clauses

```python
clauses = analysis_result["clauses"]

# Group by clause type
clauses_by_type = {}
for clause in clauses:
    clause_type = clause["clause_type"]
    if clause_type not in clauses_by_type:
        clauses_by_type[clause_type] = []
    clauses_by_type[clause_type].append(clause)

# Display
for clause_type, clause_list in clauses_by_type.items():
    st.subheader(f"{clause_type.replace('_', ' ').title()} ({len(clause_list)})")
    for clause in clause_list:
        st.write(clause["clause_text"])
```

### Displaying Statistics

```python
stats = analysis_result["statistics"]
risk_dist = stats["risk_distribution"]

col1, col2, col3 = st.columns(3)
col1.metric("Low Risk", risk_dist["low"])
col2.metric("Medium Risk", risk_dist["medium"])
col3.metric("High Risk", risk_dist["high"])
```

---

## 🚨 Important Notes

### 1. Backend Must Be Running

Frontend cannot work without backend. Always ensure:
- Backend is running on `http://localhost:8000`
- Check with: `curl http://localhost:8000/health`

### 2. Processing Time

- Small contracts (<10 clauses): ~30 seconds
- Medium contracts (10-20 clauses): ~2 minutes
- Large contracts (20+ clauses): ~4 minutes

**Show loading indicators!**

### 3. Rate Limiting

Backend automatically handles rate limiting. Frontend should:
- Be patient during processing
- Show progress indicators
- Handle timeout errors gracefully

### 4. PDF Quality

- Works best with text-based PDFs
- Scanned PDFs may need OCR (not implemented yet)
- Large PDFs (>100 pages) may timeout

---

## 🧪 Testing Your Frontend

### 1. Test with Sample Contract

Use the sample contract from tests:
```python
# From comprehensive_test.py
SAMPLE_CONTRACT = """
AGREEMENT FOR SERVICES
...
"""
```

### 2. Test API Connection

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())  # Should show {"status": "healthy"}

# Test analysis
response = requests.post(
    "http://localhost:8000/api/analyze-document",
    json={"contract_text": "Test contract..."}
)
print(response.status_code)  # Should be 200
```

### 3. Test Q&A

```python
response = requests.post(
    "http://localhost:8000/api/qa",
    json={"question": "What is a contract?", "clear_history": True}
)
print(response.json())
```

---

## 📁 File Structure for Phase 3

```
src/phase3_frontend/
├── __init__.py
├── app.py                 # Main Streamlit app
├── api_client.py          # Backend API wrapper
├── pdf_extractor.py       # PDF text extraction
├── components/
│   ├── __init__.py
│   ├── summary_tab.py     # Summary display
│   ├── clauses_tab.py     # Clauses display
│   ├── risk_tab.py        # Risk analysis display
│   ├── compliance_tab.py  # Compliance display
│   └── chat_tab.py        # Q&A chat interface
└── utils/
    ├── __init__.py
    └── formatting.py      # Helper functions
```

---

## 🎯 Quick Start Checklist

- [ ] Start backend: `python scripts/run_phase2_api.py`
- [ ] Verify backend: Visit http://localhost:8000/docs
- [ ] Create Streamlit app structure
- [ ] Implement PDF upload
- [ ] Implement API client
- [ ] Create tabs for different views
- [ ] Implement Q&A chat
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test with sample contracts
- [ ] Deploy (Streamlit Cloud/HuggingFace Spaces)

---

## 📞 Integration Support

### Common Issues

1. **Connection Error**: Backend not running
   - Solution: Start `python scripts/run_phase2_api.py`

2. **Timeout Error**: Contract too large
   - Solution: Increase timeout or split contract

3. **429 Errors**: Rate limiting (rare, backend handles)
   - Solution: Wait, backend will retry automatically

4. **Invalid JSON**: Backend returned error
   - Solution: Check backend logs, handle error gracefully

### Backend Logs

Check backend logs for debugging:
- Logs appear in console where backend is running
- Look for error messages or warnings

---

## ✅ Success Criteria

Your frontend should:
- ✅ Allow PDF upload
- ✅ Extract text from PDF
- ✅ Call backend API successfully
- ✅ Display all analysis results
- ✅ Show risk levels with color coding
- ✅ Show compliance status
- ✅ Allow Q&A chat with history
- ✅ Display citations properly
- ✅ Handle errors gracefully
- ✅ Show loading states

---

**You're ready to build Phase 3!** 🚀

Start with a simple Streamlit app, then add features incrementally.

