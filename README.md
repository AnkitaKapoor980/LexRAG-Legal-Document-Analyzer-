# LexRAG – Legal Document Analyzer

A Retrieval-Augmented Generation (RAG) system for analyzing Indian legal documents, extracting clauses, assessing risks, checking compliance, and answering legal questions.

## Project Overview

**LexRAG** is a three-phase legal document analysis system:

- **Phase 1** - Data Foundation: Legal corpus collection, preprocessing, and embedding generation
- **Phase 2** - RAG & Agents: Five specialized agents for document analysis with FastAPI backend
- **Phase 3** - Frontend: Streamlit web application for user interaction

---

## Project Structure

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

## Quick Start

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

## Running the System

### One-command Launch (Backend + Frontend)

```powershell
# Starts FastAPI backend and Streamlit UI
python scripts/run_app.py

# Frontend: http://localhost:8501
```

---

## Technologies Used

- **Phase 1**: spaCy, sentence-transformers, FAISS, BeautifulSoup
- **Phase 2**: LangChain, Groq API, FastAPI, Pydantic
- **Phase 3**: Streamlit 


