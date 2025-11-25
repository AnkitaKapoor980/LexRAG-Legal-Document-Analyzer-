# Project Structure

This document explains the organized project structure.

## 📁 Directory Structure

```
LexRAG-Legal-Document-Analyzer/
│
├── 📄 README.md                    # Main project README
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 config.yaml                  # Configuration file
├── 📄 requirements.txt             # Dependencies
├── 📄 .env                         # Environment variables (not in git)
├── 📄 .gitignore                   # Git ignore rules
│
├── 📂 src/                         # Source code
│   ├── phase1_preprocessing/       # Phase 1: Data pipeline
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_collector.py
│   │   ├── embedder.py
│   │   └── preprocessor.py
│   │
│   ├── phase2_agents/              # Phase 2: RAG & Agents
│   │   ├── __init__.py
│   │   ├── llm_client.py           # LLM abstraction
│   │   ├── retriever.py            # RAG retrieval
│   │   ├── orchestration.py        # Agent coordination
│   │   ├── README.md               # Phase 2 specific docs
│   │   ├── agents/                 # 5 agents
│   │   │   ├── clause_extractor.py
│   │   │   ├── risk_analyzer.py
│   │   │   ├── compliance_checker.py
│   │   │   ├── summarizer.py
│   │   │   └── qa_agent.py
│   │   ├── prompts/                # Prompt templates
│   │   │   └── templates.py
│   │   └── api/                    # FastAPI backend
│   │       ├── main.py
│   │       └── schemas.py
│   │
│   └── phase3_frontend/            # Phase 3: Streamlit Frontend
│       ├── README.md               # Phase 3 specific docs
│       └── streamlit_app.py        # Streamlit web application
│
│
├── 📂 data/                        # Data files
│   ├── raw/                        # Raw documents
│   │   ├── acts/
│   │   ├── cases/
│   │   └── contracts/
│   ├── processed/                  # Processed data
│   │   ├── cleaned_texts/          # Chunked JSONL files
│   │   └── metadata/               # Metadata JSON files
│   └── embeddings/                 # FAISS index
│       └── faiss_index/
│           ├── lexrag.index
│           └── metadata_map.json
│
├── 📂 scripts/                     # Utility scripts
│   ├── run_phase1_pipeline.py      # Phase 1 runner
│   ├── run_phase2_api.py           # Phase 2 API server
│   ├── run_retrieval.py            # Retrieval testing
│   └── run_app.py                  # Launch backend + frontend together
│
├── 📂 tests/                       # Test files
│   ├── phase1/                     # Phase 1 tests
│   │   ├── test_embedder.py
│   │   ├── test_preprocessor.py
│   │   └── test_retrieval.py
│   ├── phase2/                     # Phase 2 tests
│   │   ├── __init__.py
│   │   ├── test_agents.py          # Quick smoke test
│   │   └── comprehensive_test.py   # Full test suite
│   └── results/                    # Test results
│       └── phase2_test_report_*.json
│
├── 📂 docs/                        # Documentation
│   ├── README.md                   # Docs index
│   ├── PHASE1_START.md             # Phase 1 guide
│   ├── PHASE2_QUICKSTART.md        # Phase 2 guide
│   └── PHASE3_HANDOFF.md           # Phase 3 integration guide
│
└── 📂 logs/                        # Application logs
    ├── phase1_pipeline.log
    ├── phase1.log
    └── failed_downloads.txt
```

## Documentation Structure

### Main Documentation Files

1. **README.md** (Root)
   - Project overview
   - Quick start
   - Links to detailed docs

2. **docs/README.md**
   - Documentation index
   - Quick links to all guides

3. **docs/PHASE1_START.md**
   - Phase 1 setup and usage
   - Data pipeline instructions

4. **docs/PHASE2_QUICKSTART.md**
   - Phase 2 setup
   - API usage
   - Testing instructions

5. **docs/PHASE3_HANDOFF.md**
   - Complete frontend integration guide
   - API endpoints documentation
   - Implementation examples
   - UI/UX recommendations



