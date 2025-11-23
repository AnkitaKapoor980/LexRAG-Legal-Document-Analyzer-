from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.phase1_preprocessing import load_config
from src.phase1_preprocessing.embedder import load_faiss_index, retrieve_documents

SAMPLE_QUERIES = [
    "What are the provisions for contract termination?",
    "Indian Penal Code Section 302",
    "Supreme Court judgments on property rights",
]


def main(top_k: int) -> None:
    config = load_config()
    index_path = Path(config.embedding.index_path)
    metadata_path = Path(config.embedding.metadata_path)
    if not (index_path.exists() and metadata_path.exists()):
        raise FileNotFoundError("FAISS index or metadata map not found. Run the pipeline first.")

    index, metadata_map, encoder = load_faiss_index(index_path, metadata_path, config.embedding.model_name)
    for query in SAMPLE_QUERIES:
        logging.info("Query: %s", query)
        results = retrieve_documents(query, index, metadata_map, encoder, top_k=top_k)
        for rank, result in enumerate(results, start=1):
            meta = result["metadata"]
            logging.info(
                "#%d | score %.4f | %s | chunk %s",
                rank,
                result["similarity_score"],
                meta.get("title", ""),
                result["chunk_id"],
            )
            logging.info("Snippet: %s", result["text"][:200] + "...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    parser = argparse.ArgumentParser(description="Validate FAISS retrieval quality.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to display per query.")
    args = parser.parse_args()
    main(top_k=args.top_k)
