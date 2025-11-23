# LexRAG – Legal Document Analyzer

LexRAG is a Retrieval-Augmented Generation (RAG) pipeline tailored for Indian legal research. This repository contains all three phases of the system, with Phase 1 (data foundation) fully implemented in this deliverable.

## Repository Layout

```
lexrag/
├── data/                    # Raw, processed, and embedded corpora
├── src/
│   ├── phase1_preprocessing  # Data collection, cleaning, embeddings
│   ├── phase2_agents         # (Placeholder) RAG agents
│   └── phase3_frontend       # (Placeholder) UI
├── scripts/                 # Helper scripts (pipeline + validation)
├── tests/                   # Unit tests
├── config.yaml              # Runtime configuration
└── requirements.txt         # Dependencies
```

## Phase 1 Overview

Phase 1 consolidates three legal data sources:

- **India Code**: 10–15 major acts
- **Indian Kanoon**: 50–100 case law documents
- **CUAD**: Contract samples

The pipeline performs:

1. **Collection** – HTTP scraping/downloading with rate limiting, resuming, and metadata capture.
2. **Preprocessing** – OCR/PDF extraction, cleaning, tokenization, and chunking with contextual overlap.
3. **Embedding** – Sentence-transformer embeddings stored in a FAISS vector index with metadata mapping.

Outputs are persisted under `data/processed/` and `data/embeddings/` for reuse.

## Getting Started

1. **Create environment & install dependencies**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure**

   Update `config.yaml` to adjust URLs, chunk sizes, embedding model, or directories.

3. **Run Phase 1 pipeline**

   ```bash
   python scripts/run_phase1_pipeline.py
   ```

   Use `--force-refresh` to re-run collection or `--skip-embeddings` to stop after preprocessing.

   You can also temporarily override the embedding model at runtime without editing `config.yaml` by setting the
   `EMBEDDING_MODEL` environment variable or using the new `--embedding-model` CLI flag. If you change the model,
   remember to rebuild embeddings (use `--force-refresh` or remove existing index files) because embedding vectors
   and dimensions will differ between models.

4. **Validate retrieval quality**

   ```bash
   python scripts/run_retrieval.py --top-k 5
   ```

## Testing

```
pytest
```

Unit tests cover preprocessing utilities, embedding generation, and retrieval helpers (with mocking where external services are involved).

## Phase 2 & 3 Collaboration

- See `INTEGRATION_GUIDE.md` for detailed instructions on consuming the FAISS index and metadata (Phase 2) and wired data access for the frontend (Phase 3).
- Placeholders in `src/phase2_agents/` and `src/phase3_frontend/` outline integration contracts and expected entry points.

## Notes

- All scraping obeys robots.txt guidance and uses configurable rate limiting.
- The pipeline is resumable; already-downloaded files are skipped unless `--force-refresh` is provided.
- Logs go to `logs/phase1.log` and stdout for quick triage.

For questions or contributions, please open an issue or PR referencing the relevant phase. Happy researching!

