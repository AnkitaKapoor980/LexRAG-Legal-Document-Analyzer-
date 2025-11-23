# Phase 2 – RAG & Agent Layer

Phase 2 implements the RAG pipeline and five specialized agents for legal document analysis.

## ✅ Implementation Complete

### Components

1. **RAG Retriever** (`retriever.py`)
   - Wraps Phase 1 FAISS index
   - Retrieves relevant legal context
   - Formats context for LLM prompts

2. **LLM Client** (`llm_client.py`)
   - Unified interface for Groq/HuggingFace APIs
   - Supports Groq API (recommended for free tier)
   - Configurable via environment variables

3. **Five Agents** (`agents/`)
   - **Clause Extractor**: Identifies and extracts contract clauses
   - **Risk Analyzer**: Assesses risk levels (low/medium/high)
   - **Compliance Checker**: Verifies compliance with Indian laws using RAG
   - **Summarizer**: Generates plain-language summaries
   - **Q&A Agent**: Answers legal questions with citations

4. **Orchestration** (`orchestration.py`)
   - Coordinates all agents
   - Full document analysis pipeline
   - Individual agent access

5. **FastAPI Backend** (`api/`)
   - RESTful API endpoints
   - Auto-generated Swagger docs
   - Request/response validation

## 🚀 Quick Start

### 1. Setup Environment

```powershell
# Install dependencies
pip install -r requirements.txt

# Create .env file with Groq API key
# GROQ_API_KEY=your_key_here
# GROQ_MODEL=llama-3.1-8b-instant
```

### 2. Test Agents

```powershell
python -m src.phase2_agents.test_agents
```

### 3. Start API Server

```powershell
uvicorn src.phase2_agents.api.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs (Swagger UI)

## 📡 API Endpoints

### Individual Agents
- `POST /api/extract-clauses` - Extract clauses from contract
- `POST /api/analyze-risk` - Analyze risk of a clause
- `POST /api/check-compliance` - Check clause compliance
- `POST /api/summarize` - Generate contract summary
- `POST /api/qa` - Answer legal questions

### Unified Endpoint
- `POST /api/analyze-document` - Full document analysis pipeline

### Health Check
- `GET /health` - Service health status

## 📁 Structure

```
src/phase2_agents/
├── __init__.py
├── llm_client.py          # LLM abstraction
├── retriever.py           # RAG retrieval wrapper
├── orchestration.py       # Agent coordination
├── test_agents.py         # Smoke tests
├── agents/
│   ├── clause_extractor.py
│   ├── risk_analyzer.py
│   ├── compliance_checker.py
│   ├── summarizer.py
│   └── qa_agent.py
├── prompts/
│   └── templates.py       # Prompt templates
└── api/
    ├── main.py            # FastAPI app
    └── schemas.py         # Request/response models
```

## 🔧 Configuration

Set environment variables in `.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

## 📝 Usage Examples

### Python API

```python
from src.phase2_agents.orchestration import get_orchestrator

orchestrator = get_orchestrator()
result = orchestrator.analyze_document(contract_text)
```

### REST API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze-document",
    json={"contract_text": "Your contract text here..."}
)
print(response.json())
```

## 🧪 Testing

Run smoke tests:
```powershell
python -m src.phase2_agents.test_agents
```

## 🔗 Integration with Phase 1

Phase 2 uses Phase 1's FAISS index:
- Index path: `data/embeddings/faiss_index/lexrag.index`
- Metadata: `data/embeddings/faiss_index/metadata_map.json`
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-d)

## 🎯 Next Steps (Phase 3)

Phase 3 frontend should:
1. Call FastAPI endpoints at `http://localhost:8000`
2. Use `/api/analyze-document` for full analysis
3. Use individual endpoints for specific tasks
4. Display results with proper formatting

## 📚 Documentation

- API docs: http://localhost:8000/docs (when server is running)
- See `docs/PHASE2_HANDOFF.md` for detailed integration guide
