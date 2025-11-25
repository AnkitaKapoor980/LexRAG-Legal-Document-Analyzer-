# Phase 2 Quick Start Guide

## Overview

Phase 2 implements RAG (Retrieval-Augmented Generation) pipeline with 5 specialized agents for legal document analysis.

**Components**:
- RAG Retriever (FAISS integration)
- LLM Client (Groq/HuggingFace)
- 5 Agents (Clause Extractor, Risk Analyzer, Compliance Checker, Summarizer, Q&A)
- FastAPI Backend
- Agent Orchestration

---

## Quick Setup

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Set Up Environment

Create `.env` file in project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

**Get Groq API Key**: https://console.groq.com/ (Free tier: ~14,400 requests/day)

### 3. Verify Phase 1 Data
```powershell
python scripts/run_retrieval.py --top-k 3
```

---

## Running the API

### Start Backend Server
```powershell
python scripts/run_phase2_api.py
# Or: uvicorn src.phase2_agents.api.main:app --reload --port 8000
```

**API Docs**: http://localhost:8000/docs

---

## API Endpoints

### Main Endpoint: Full Document Analysis
```python
POST /api/analyze-document
{
  "contract_text": "Your contract text...",
  "extract_clauses": true,
  "analyze_risks": true,
  "check_compliance": true,
  "generate_summary": true
}
```

### Q&A Endpoint
```python
POST /api/qa
{
  "question": "What is the termination clause?",
  "clear_history": false
}
```

### Other Endpoints
- `POST /api/extract-clauses` - Extract clauses only
- `POST /api/analyze-risk` - Analyze risk of single clause
- `POST /api/check-compliance` - Check compliance
- `POST /api/summarize` - Generate summary
- `GET /health` - Health check

---

## Testing

### Quick Smoke Test
```powershell
python -m pytest tests/phase2/test_agents.py -v
```

### Comprehensive Test (with real contract)
```powershell
python -m pytest tests/phase2/comprehensive_test.py -v
```

**Test Results**: Saved to `tests/results/`

---

## Project Structure

```
src/phase2_agents/
├── llm_client.py          # LLM abstraction
├── retriever.py           # RAG retrieval
├── orchestration.py       # Agent coordination
├── agents/                # 5 agents
├── prompts/               # Prompt templates
└── api/                   # FastAPI backend

tests/
├── phase1/                # Phase 1 tests
├── phase2/                # Phase 2 tests
└── results/               # Test results
```

---

## Key Features

- ✅ **Rate Limiting**: Automatic retry with delays (2.5s between requests)
- ✅ **Error Handling**: Robust error handling and recovery
- ✅ **RAG Integration**: Uses Phase 1 FAISS index (2,669 chunks)
- ✅ **JSON Responses**: Standardized response format
- ✅ **CORS Enabled**: Ready for frontend integration

---

## Performance

- **Small contracts** (<10 clauses): ~30 seconds
- **Medium contracts** (10-20 clauses): ~2 minutes
- **Large contracts** (20+ clauses): ~4 minutes

**Note**: Processing time depends on contract size and API rate limits.

---

## Next Steps

See **[Phase 3 Integration Guide](PHASE3_HANDOFF.md)** for frontend integration details.

