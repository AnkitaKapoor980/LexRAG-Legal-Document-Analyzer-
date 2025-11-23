# LexRAG Integration Guide

This document explains how Phase 2 (RAG & agents) and Phase 3 (frontend) teams can consume artifacts created by Phase 1.

## Phase 2 – RAG Agents

### Loading the FAISS Index

```python
from src.phase1_preprocessing.embedder import load_faiss_index, retrieve_documents
from src.phase1_preprocessing.config import load_config

config = load_config()
index, metadata_map, encoder = load_faiss_index(
    config.embedding.index_path,
    metadata_path=config.embedding.metadata_path,
    model_name=config.embedding.model_name,
)
```

### Retrieving Relevant Chunks

```python
query = "breach of contract remedies"
results = retrieve_documents(
    query=query,
    index=index,
    metadata_map=metadata_map,
    encoder=encoder,
    top_k=5,
)

for item in results:
    print(item["chunk_id"], item["similarity_score"])
    print(item["metadata"]["title"])
    print(item["text"])
```

Each result dictionary contains:

- `chunk_id`
- `text` (normalized chunk)
- `metadata` (title, section, year, jurisdiction, document type, etc.)
- `chunk_order` (position in document)
- `similarity_score` (cosine similarity)

Use `metadata["source_path"]` to retrieve the original document if needed.

### Suggested Workflow

1. Encode user query with the same sentence-transformer model used in Phase 1.
2. Retrieve top-k chunks.
3. Use metadata for citation strings (`title`, `section`, `year`, `chunk_id`).
4. Pass concatenated chunks to downstream LLM prompts.

## Phase 3 – Frontend

### Directory Structure Reference

- `data/raw/` – Original documents grouped by type.
- `data/processed/cleaned_texts/` – JSON Lines files with chunked, cleaned text per document.
- `data/processed/metadata/` – Document-level metadata (`*.json`).
- `data/embeddings/faiss_index/` – FAISS index file plus `metadata_map.json`.

### Accessing Processed Documents

Each file in `data/processed/cleaned_texts/` follows:

```json
{"chunk_id": "ipc_1860_chunk_0001", "text": "...", "chunk_order": 1, "document_id": "ipc_1860"}
```

The paired metadata file (`data/processed/metadata/ipc_1860.json`) contains:

```json
{
  "document_id": "ipc_1860",
  "title": "Indian Penal Code, 1860",
  "document_type": "act",
  "source_url": "https://www.indiacode.nic.in/...",
  "jurisdiction": "India",
  "year": 1860,
  "sections": ["302", "303"],
  "chunk_count": 48
}
```

### Chunk ID System

`<slug>_chunk_<NNNN>`

- `slug` is derived from document title + year.
- Zero-padded chunk index preserves ordering.
- Use chunk IDs for UI citations (e.g., “IPC 1860 – chunk 0012”).

### Display Suggestions

- Show snippet text plus metadata (title, section, year).
- Provide “open original” link leveraging `metadata["source_url"]`.
- Highlight matched query terms in the chunk text.

## General Tips

- Always load configuration through `load_config()` to respect user overrides.
- Paths in config are relative to repo root; use `Path(config.paths.root_dir).resolve()` if needed.
- Logs live in `logs/phase1.log`; monitor them during integration to understand upstream processing decisions.

Ping the Phase 1 owner if you need additional metadata fields or indexing strategies.

