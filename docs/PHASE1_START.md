# Phase 1 — Quick Start & Verification

This document explains how to start Phase 1 (data collection, preprocessing, and embedding) and how to verify it's working correctly. It assumes you're at the repository root (where `config.yaml` and `requirements.txt` live).

Prerequisites
- Python 3.10+ installed (this repo used Python 3.12 in tests).
- Internet access to download sentence-transformers models (first run).
- Optional: `poppler` if you will OCR PDFs via `pdf2image`.

1) Create a virtual environment and install dependencies

PowerShell (recommended):
```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
# Download spaCy English model used by the preprocessor
python -m spacy download en_core_web_sm
```

2) (Optional) Choose an embedding model
- Default is configured in `config.yaml` under `embedding.model_name` (currently `sentence-transformers/all-MiniLM-L6-v2`).
- You can temporarily override per-run using:
  - environment variable `EMBEDDING_MODEL`, or
  - the CLI flag `--embedding-model` on `scripts/run_phase1_pipeline.py`.
- Example lighter model: `sentence-transformers/all-MiniLM-L3-v2` (faster, slightly lower accuracy).

3) Run the Phase 1 pipeline (full rebuild)

Notes before running:
- The pipeline imports project modules as `src.*`. To ensure imports resolve, run it as a module with `-m` or set `PYTHONPATH` to the repo root.

Run (module form — preferred):
```powershell
C:/Python/Python312/python.exe -m scripts.run_phase1_pipeline --force-refresh --embedding-model "sentence-transformers/all-MiniLM-L3-v2"
```

Or set PYTHONPATH and run script directly:
```powershell
# Uncomment to set PYTHONPATH to the repo root if needed
$env:PYTHONPATH = (Resolve-Path .).Path
C:/Python/Python312/python.exe scripts/run_phase1_pipeline.py --force-refresh --embedding-model "sentence-transformers/all-MiniLM-L3-v2"
```

Flags explained:
- `--force-refresh` : re-run collection / preprocessing / embedding and overwrite outputs.
- `--skip-embeddings`: stop after preprocessing (useful if you don't want to rebuild embeddings).
- `--embedding-model`: temporarily set the model for this run (same as `EMBEDDING_MODEL`).

4) Verify outputs (quick checklist)

- Logs: `logs/phase1_pipeline.log` — open and scan for ERROR/CRITICAL entries.
- Preprocessed files: `data/processed/cleaned_texts/` — should contain `*.jsonl` files (chunked texts).
- Metadata: `data/processed/metadata/` — JSON files (one per document) with `local_path` and `chunk_count`.
- Embeddings / FAISS index:
  - `data/embeddings/faiss_index/lexrag.index` — the FAISS index file.
  - `data/embeddings/faiss_index/metadata_map.json` — JSON array mapping index rows to chunk metadata.

Quick filesystem checks (PowerShell):
```powershell
# Check processed text files
Get-ChildItem -Path data/processed/cleaned_texts -Filter *.jsonl | Select-Object Name, Length
# Check metadata files
Get-ChildItem -Path data/processed/metadata -Filter *.json | Select-Object Name, Length
# Check index files
Test-Path data/embeddings/faiss_index/lexrag.index; Test-Path data/embeddings/faiss_index/metadata_map.json
```

5) Smoke-test retrieval

If the index and metadata exist, run the retrieval script to verify search works:
```powershell
C:/Python/Python312/python.exe scripts/run_retrieval.py --top-k 5
# or: C:/Python/Python312/python.exe -m scripts.run_retrieval --top-k 5
```

You should see logging lines showing queries and returned snippets. If no results are returned, verify the index file exists and that `metadata_map.json` has entries.

6) Common issues & fixes

- ModuleNotFoundError: No module named 'src'
  - Run the pipeline using `-m` from repo root or set `PYTHONPATH` to the repo root before running the script (see section 3).

- FAISS installation errors on Windows
  - Some Windows setups cannot install `faiss-cpu` via pip. Use conda: `conda install -c conda-forge faiss-cpu` or run on WSL/Ubuntu.

- Binary incompatibility (numpy/pandas)
  - If you see "numpy.dtype size changed" errors, pin compatible versions (e.g., `numpy==1.26.4`, `pandas==2.2.3`) or recreate the venv and reinstall.

- Model download stalls or fails
  - Ensure network access and disk space. The sentence-transformers models download to the huggingface cache by default (~hundreds of MBs). If firewall or offline, pre-download the model on another machine and set HF_HOME/HUGGINGFACE_HUB_CACHE.

7) Rebuilding after changing models
- If you change `EMBEDDING_MODEL` (via env var, CLI, or in `config.yaml`), you MUST rebuild embeddings and the FAISS index — the code stores raw vectors and the index expects the vectors from the same model.
- Use `--force-refresh` when running the pipeline to force a rebuild.

8) Running tests (sanity before integration)
```powershell
C:/Python/Python312/python.exe -m pytest -q
```

Notes about this repository (what I changed while auditing)
- Added `EMBEDDING_MODEL` support for runtime overrides in `src/phase1_preprocessing/embedder.py`.
- Added a `--embedding-model` CLI flag to `scripts/run_phase1_pipeline.py`.
- Renamed the scripts retrieval validator from `scripts/test_retrieval.py` to `scripts/run_retrieval.py` to avoid pytest name collisions.
- Fixed a small whitespace bug in `src/phase1_preprocessing/preprocessor.py` (improved `clean_text()` behavior).

If everything in Phase 1 runs end-to-end and retrieval returns sensible snippets for the sample queries, Phase 1 is ready to be integrated with Phase 2 (agents) and Phase 3 (frontend). When integrating:
- Provide the FAISS index path and `metadata_map.json` location to Phase 2.
- Share the embedding model name and embedding dimension so agents can embed queries the same way.

If you want, I can:
- Run the full pipeline here and report logs, produced file counts, and a retrieval sample (will take time and download models).
- Add a small integration README snippet that documents the exact contract for Phase 2 (index path, metadata shape, sample retrieval API). 

---
End of document.
