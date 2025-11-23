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

