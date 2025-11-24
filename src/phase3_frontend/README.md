# Phase 3 — Simple Frontend (LexRAG)

This folder contains a minimal FastAPI-based UI to try retrieval locally. It is intentionally small and depends on the project's existing embedding/FAISS code.

Prerequisites
- Python environment with the project's `requirements.txt` installed (see project root).
- A built FAISS index and metadata (created by the phase 1 pipeline). The UI reads index paths from `config.yaml`.


Run locally (two options)

Option A — Streamlit frontend (recommended for Phase 3 UX)

1. From the project root, install requirements (if not already):

```powershell
pip install -r requirements.txt
pip install streamlit pdfplumber
```

2. Run the Streamlit app:

```powershell
streamlit run src/phase3_frontend/streamlit_app.py
```

3. Open the URL Streamlit prints (usually `http://localhost:8501`).

Option B — FastAPI demo UI (keeps simple HTML pages)

1. Install requirements (if not already). If you plan to submit forms via HTML, either install `python-multipart` or use the Streamlit app.

```powershell
pip install -r requirements.txt
# If you want to use the HTML form UI via uvicorn, install the multipart helper:
pip install python-multipart
```

2. Start FastAPI demo UI (if you installed multipart):

```powershell
uvicorn src.phase3_frontend.app:app --reload --port 8000
```

3. Open `http://localhost:8000` in your browser. The FastAPI demo will attempt to load the FAISS index configured in `config.yaml`.

Notes
- The Streamlit app follows the `PHASE3_HANDOFF.md` flow: upload PDF → extract text → call `/api/analyze-document` → display results in tabs and allow Q&A.
- The FastAPI HTML UI is left available for quick index inspection; I modified it to avoid raising an import-time error when `python-multipart` is not installed.

Notes
- The UI loads the SentenceTransformer encoder during index load; expect model download time on first run.
- This is a simple dev-facing UI — it is not hardened for production.
# Phase 3 – Frontend Interface

This folder is reserved for Member C, responsible for building the LexRAG user interface.

## Data Inputs

- Processed chunks: `data/processed/cleaned_texts/`
- Metadata: `data/processed/metadata/`
- Retrieval API: Use the Phase 2 agent layer (once available) or directly call `retrieve_documents` from `src.phase1_preprocessing.embedder`.

## UX Guidelines

- Display retrieved chunks with title, section, year, and chunk ID.
- Provide citation links back to the original source URL.
- Offer filters by document type (act, case, contract) and year.

## Suggested Stack

Feel free to choose any framework (React, Vue, FastAPI + HTMX, etc.) as long as it can consume the retrieval API. Keep frontend assets under this directory and document build steps in a local README.

