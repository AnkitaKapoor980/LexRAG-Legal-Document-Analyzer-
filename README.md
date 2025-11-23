# LexRAG – Legal Document Analyzer

A Retrieval-Augmented Generation (RAG) system for analyzing Indian legal documents, extracting clauses, assessing risks, checking compliance, and answering legal questions.

## 🎯 Project Overview

**LexRAG** is a three-phase legal document analysis system:

- **Phase 1** - Data Foundation: Legal corpus collection, preprocessing, and embedding generation
- **Phase 2** - RAG & Agents: Five specialized agents for document analysis with FastAPI backend
- **Phase 3** - Frontend: Streamlit web application for user interaction

---

## 📁 Project Structure

```
LexRAG-Legal-Document-Analyzer/
├── src/
│   ├── phase1_preprocessing/  # Data collection, cleaning, embeddings
│   ├── phase2_agents/         # RAG agents & FastAPI backend
│   └── phase3_frontend/       # Streamlit frontend (placeholder)
├── data/
│   ├── raw/                   # Raw legal documents
│   ├── processed/             # Cleaned and chunked texts
│   └── embeddings/            # FAISS index and metadata
├── scripts/                   # Utility scripts
├── tests/
│   ├── phase1/                # Phase 1 tests
│   ├── phase2/                # Phase 2 tests
│   └── results/               # Test results
├── docs/                      # Documentation
├── logs/                      # Application logs
├── config.yaml                # Configuration
└── requirements.txt           # Dependencies
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment
- Groq API key (free tier available)

### Installation

1. **Clone repository** (if applicable) or navigate to project directory

2. **Create virtual environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Set up environment variables**:
   Create `.env` file in project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   ```

---

## 📚 Documentation

See **[docs/README.md](docs/README.md)** for complete documentation:

- **[Phase 1 Start Guide](docs/PHASE1_START.md)** - Run data pipeline
- **[Phase 2 Quick Start](docs/PHASE2_QUICKSTART.md)** - API setup and usage
- **[Phase 3 Integration Guide](docs/PHASE3_HANDOFF.md)** - Frontend integration

---

## 🏃 Running the System

### Phase 1: Data Pipeline (Already Complete)

```powershell
# Run Phase 1 pipeline (if needed)
python scripts/run_phase1_pipeline.py --force-refresh

# Test retrieval
python scripts/run_retrieval.py --top-k 5
```

### Phase 2: Start API Backend

```powershell
# Start FastAPI server
python scripts/run_phase2_api.py

# API will be available at:
# http://localhost:8000/docs
```

### Phase 3: Frontend (To Be Built)

```powershell
# Once implemented:
streamlit run src/phase3_frontend/app.py
```

---

## 🧪 Testing

### Phase 1 Tests
```powershell
pytest tests/ -v
```

### Phase 2 Tests
```powershell
# Quick smoke test
python -m pytest tests/phase2/test_agents.py -v

# Comprehensive test with real contract
python -m pytest tests/phase2/comprehensive_test.py -v
```

---

## 🔧 Configuration

Edit `config.yaml` to adjust:
- Embedding model
- Chunk sizes
- Data sources
- Paths

---

## 📊 Current Status

- ✅ **Phase 1**: Complete - FAISS index with 2,669 chunks ready
- ✅ **Phase 2**: Complete - All 5 agents functional, API running
- ⏳ **Phase 3**: To be implemented - Frontend integration needed

---

## 🛠️ Technologies Used

- **Phase 1**: spaCy, sentence-transformers, FAISS, BeautifulSoup
- **Phase 2**: LangChain, Groq API, FastAPI, Pydantic
- **Phase 3**: Streamlit (planned)

---

## 📝 License & Notes

- All scraping respects robots.txt
- Rate limiting implemented for API calls
- Free tier Groq API suitable for development/demo

---

## 🤝 Contributing

See documentation in `docs/` folder for each phase's implementation details.

---

**For detailed setup and usage, see [docs/README.md](docs/README.md)**
