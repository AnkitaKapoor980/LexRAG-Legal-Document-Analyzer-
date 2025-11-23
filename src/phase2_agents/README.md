# Phase 2 – Agent & RAG Integration

This directory is reserved for Member B, who will implement:

- Query understanding and routing agents
- Prompt orchestration for LLM calls
- Retrieval-Augmented Generation logic using the FAISS index produced in Phase 1

## Expected Entry Points

- `src/phase1_preprocessing/embedder.py` exposes `load_faiss_index` and `retrieve_documents`.
- Use these helpers to fetch relevant chunks given a user query.

## Suggested Structure

```
src/phase2_agents/
├── __init__.py
├── agent.py
├── retriever.py
└── prompts/
```

Keep dependencies isolated by adding any Phase 2–specific requirements to a dedicated `requirements-phase2.txt` (or update the main requirements if shared).

