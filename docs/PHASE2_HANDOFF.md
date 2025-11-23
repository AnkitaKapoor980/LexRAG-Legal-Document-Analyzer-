# Phase 2 Handoff — RAG & Agent Layer (what Phase 1 supplies and what Phase 2 needs)

This file documents exactly what Phase 1 produced, the data shapes and runtime contracts Phase 2 will rely on, and a short checklist of recommended additions and verification steps to ensure Phase 2 can integrate and run smoothly.

## Summary (quick)
- Phase 1 produced a FAISS index and a metadata map for retrieval, plus processed chunk JSONL files (cleaned texts + metadata) ready for RAG.
- Index: `data/embeddings/faiss_index/lexrag.index`
- Metadata map: `data/embeddings/faiss_index/metadata_map.json`
- Processed chunks directory: `data/processed/cleaned_texts/` (many `*.jsonl` files)
- Embedding model used for the last run: `sentence-transformers/all-MiniLM-L6-v2` (384-d vectors)
- Index type: `IndexFlatIP` (inner product; Phase 1 normalized vectors -> cosine-like similarity)

## Phase 1 artifacts (explicit)
1. FAISS index
   - Path: `data/embeddings/faiss_index/lexrag.index`
   - Class: IndexFlatIP
   - ntotal (vectors): 2669 (as of latest run)
   - vector dimension: 384
   - Note: Index was built with normalized embeddings (config.normalize_embeddings: true). Matching normalization is necessary at query time.

2. Metadata map (array)
   - Path: `data/embeddings/faiss_index/metadata_map.json`
   - Structure: list of objects like:
     {
       "chunk_id": str,
       "text": str,
       "metadata": {"source_path": str, "document_type": str, "title": str, ...},
       "chunk_order": int
     }
   - Use: mapping index result index -> chunk + metadata for building agent prompts and provenance.

3. Processed chunk files (per-document `.jsonl`)
   - Directory: `data/processed/cleaned_texts/`
   - Each `.jsonl` file contains one or more JSON lines with fields at least: `chunk_id`, `text`, `chunk_order`, `metadata`.
   - Example file names include acts and cases and contract placeholders (e.g. `contract_act_1872.jsonl`, `1048577.jsonl`, `code_of_civil_procedure_1908.jsonl`).

4. Source/raw data references
   - Raw directories exist: `data/raw/acts/`, `data/raw/cases/`, `data/raw/contracts/` (some files are placeholders added to make Phase 1 deterministic).
   - Metadata contains `source_path` pointing to the original raw file.

5. Config that matters to Phase 2 (from `config.yaml`)
   - `embedding.model_name` default: `sentence-transformers/all-MiniLM-L6-v2` (384-d)
   - `embedding.faiss_index_type`: `IndexFlatIP`
   - `embedding.normalize_embeddings`: true
   - `preprocessing.chunk_size`: 450
   - `preprocessing.chunk_overlap`: 75
   - `preprocessing.spacy_model`: `en_core_web_sm`
   - `paths.embeddings_dir` and `paths.processed_text_dir` locations noted above

6. Retrieval helper functions (code contracts)
   - `src/phase1_preprocessing/embedder.py` provides:
     - `load_faiss_index(index_path, metadata_path, model_name)` -> (faiss.Index, metadata, encoder)
     - `retrieve_documents(query, index, metadata_map, encoder, top_k=5)` -> list of dicts: `{chunk_id, text, metadata, chunk_order, similarity_score}`
   - `EmbeddingGenerator.build()` can be used to rebuild index when needed.

7. CLI / runtime overrides
   - Pipeline supports `--embedding-model` flag (scripts runner sets `EMBEDDING_MODEL` env var) and Phase 1 embedder checks `EMBEDDING_MODEL` env var.
   - Useful for ensuring Phase 2 uses the same embedding model for query encoding.

## What Phase 2 must ensure (compatibility checklist)
1. Embedding model parity
   - Query embeddings MUST use the same model family and behavior (dimension, normalization) as the index was built with, or the FAISS index must be rebuilt with the Phase 2 model.
   - Options:
     - Use `sentence-transformers/all-MiniLM-L6-v2` at query time (recommended for parity).
     - If you choose a lighter/heavier model, check that the embedding dimension equals 384 OR rebuild the FAISS index.
   - Use existing env var override: set `EMBEDDING_MODEL` or pass `--embedding-model` to the Phase 1 script before rebuilding.

2. Normalization
   - If `normalize_embeddings` was True during index build, ensure the encoder used for queries also normalizes embeddings (cosine semantics). The repo's `retrieve_documents()` uses `normalize_embeddings=True` for queries — confirm the actual encoder call in Phase 2 does the same.

3. Retrieval parameters
   - Top-K: choose `top_k` per agent (Clause Extractor may use top 5, Compliance Checker may use top 10).
   - Score interpretation: similarity_score is inner product on normalized vectors (approx cosine) — near 1.0 = close match.

4. Metadata & provenance
   - Agents that need source evidence should use `metadata.source_path`, `metadata.title`, and `chunk_id` to provide citations in outputs.
   - If Phase 2 needs chunk offsets (char/byte positions) for exact clause mapping, add `char_start`/`char_end` to chunk metadata when reprocessing.

5. Chunk granularity
   - Current chunk size (450 tokens / characters depending) and 75 overlap is a medium setting. Clause-level extraction might require smaller chunks (200–300). If agents need higher recall for short clauses, consider running a re-chunker or clause splitting step.

6. Unit tests & fixtures
   - Provide 2–3 small contract files (in `data/processed/cleaned_texts/` or `tests/fixtures/`) with known clauses and expected outputs for: Clause Extractor, Risk Analyzer, Compliance Checker, Summarizer, QnA.
   - Phase 2 unit tests should call `src/phase1_preprocessing/embedder.load_faiss_index()` and `retrieve_documents()` to assert that retrieved contexts match expected chunk ids/titles.

7. Rebuild strategy
   - If Phase 2 decides on a different embedding model, rebuild index by running:

```powershell
# from repo root (powershell)
python -m scripts.run_phase1_pipeline --force-refresh --embedding-model "sentence-transformers/<chosen-model>"
```

- Or, use EmbeddingGenerator.build() in an interactive script to rebuild and write `lexrag.index` and `metadata_map.json`.

8. FAISS on Windows
   - The repo uses `faiss` wheels; on some Windows machines, installing via conda may be needed. If Phase 2 runs into FAISS install issues, prefer conda-forge `faiss-cpu`.

## Suggested Phase 2 test plan (smoke + unit)
1. Smoke retrieval test (manual):
   - Pick a short query relevant to contracts/cases, e.g. `"arbitration clause assignment"`.
   - Run a small Python script that:
     - Loads index and metadata via `load_faiss_index()` with the same model name.
     - Calls `retrieve_documents(query, index, metadata_map, encoder, top_k=5)`.
     - Prints returned `chunk_id`, `metadata.title`, and `similarity_score`.

2. Agent unit tests (per agent)
   - Clause Extractor: assert that given a small contract chunk, the agent finds clause text matching a regex and returns JSON with clause_type and offsets.
   - Risk Analyzer: mock LLM responses or use a deterministic small model; assert classification in {low, medium, high} for sample clauses.
   - Compliance Checker: using retrieval results, assert that the agent can find the cited statute or case in `metadata.title` or chunk text.
   - Summarizer and QnA: smoke test with 1-2 questions and expect non-empty, evidence-backed responses.

3. Integration test
   - Full RAG + Agent flow on one sample contract: retrieve contexts (top 5), run Clause Extractor, pass clauses to Risk Analyzer & Compliance Checker, then summarize and run QnA.

## Useful commands & code snippets
- Load index & run basic retrieval (Python interactive):

```python
from src.phase1_preprocessing.embedder import load_faiss_index, retrieve_documents
index, metadata, encoder = load_faiss_index('data/embeddings/faiss_index/lexrag.index', 'data/embeddings/faiss_index/metadata_map.json', 'sentence-transformers/all-MiniLM-L6-v2')
results = retrieve_documents('arbitration clause', index, metadata, encoder, top_k=5)
for r in results:
    print(r['chunk_id'], r['metadata'].get('title'), r['similarity_score'])
    print(r['text'][:400])
    print('---')
```

- Rebuild the index (if you change embedding model):

```powershell
python -m scripts.run_phase1_pipeline --force-refresh --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
```

- Run Phase 1 pipeline (fast, from repo root):

```powershell
python -m scripts.run_phase1_pipeline --force-refresh
```

## Recommended small improvements (Phase 1 -> Phase 2 handoff)
- Add a `tests/fixtures/contracts/` folder with 2–3 small contract JSONL files and expected clause/risk labels for deterministic unit tests.
- Add `char_start`/`char_end` to `metadata` for each chunk when reprocessing (helps clause provenance).
- Add a `scripts/run_retrieval.py` example (if not already present) showing a minimal retrieval + print template for Phase 2 devs. (There is a `scripts/run_retrieval.py` in the repo — verify its location and usage.)
- Document the embedding model and index dimension in `README.md` or `docs/PHASE2_HANDOFF.md` (done here) so Phase 2 teams do not accidentally mismatch models.

## Data privacy & licensing notes
- Check license / copyright for raw sources if Phase 2 plans to expose model outputs externally.
- Some raw data placeholders were used to make Phase 1 deterministic — replace with approved datasets for production use.

## Contact points in repo (where to plug Phase 2 code)
- Retrieval & embeddings: `src/phase1_preprocessing/embedder.py`
- Preprocessed chunks: `data/processed/cleaned_texts/` (read these to construct per-document prompts if needed)
- Config file: `config.yaml` (Phase 2 can reuse this to find paths and embedding settings)
- Pipeline runner: `scripts/run_phase1_pipeline.py` (re-indexing & reprocessing)

## Final checklist for Phase 2 kickoff
- [ ] Confirm embedding model for queries (use same as index or rebuild index).
- [ ] Add or confirm small contract fixtures for unit tests.
- [ ] Verify FAISS works on Phase 2 dev machines (conda fallback if pip wheel fails on Windows).
- [ ] Run retrieval smoke test and verify top results and `similarity_score` semantics.
- [ ] Confirm metadata fields needed by agents (add `char_start`/`char_end` if required).


If you want, I can now:
- run a quick retrieval smoke test with a sample query and paste the outputs; or
- add small test fixtures (2 lightweight sample contracts) under `tests/fixtures/` to help Phase 2 unit tests.

Pick which next step you want and I'll do it.