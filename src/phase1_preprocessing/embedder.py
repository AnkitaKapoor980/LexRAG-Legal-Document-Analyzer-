from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .config import AppConfig

logger = logging.getLogger(__name__)


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    metadata: Dict[str, str]
    chunk_order: int


class EmbeddingGenerator:
    """Generates embeddings for chunked texts and builds FAISS indexes."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.paths = config.paths
        self.embedding_cfg = config.embedding
        # Allow overriding the configured model with an environment variable
        model_name = os.getenv("EMBEDDING_MODEL", self.embedding_cfg.model_name)
        self.encoder = SentenceTransformer(model_name)
        logger.info("Loaded embedding model: %s", model_name)

    def _load_chunks(self) -> List[ChunkRecord]:
        chunks: List[ChunkRecord] = []
        files = list(sorted(self.paths.processed_text_dir.glob("*.jsonl")))
        for file_path in tqdm(files, desc="Loading chunks"):
            with file_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    data = json.loads(line)
                    chunks.append(
                        ChunkRecord(
                            chunk_id=data["chunk_id"],
                            text=data["text"],
                            chunk_order=data["chunk_order"],
                            metadata=data.get("metadata", {}),
                        )
                    )
        logger.info("Loaded %d chunks from processed data", len(chunks))
        return chunks

    def _encode_chunks(self, texts: Iterable[str]) -> np.ndarray:
        embeddings = self.encoder.encode(
            list(texts), show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=self.embedding_cfg.normalize_embeddings
        )
        return embeddings.astype("float32")

    def _build_index(self, vectors: np.ndarray) -> faiss.Index:
        dim = vectors.shape[1]
        if self.embedding_cfg.faiss_index_type == "IndexFlatL2":
            index = faiss.IndexFlatL2(dim)
        else:
            index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        return index

    def build(self) -> Tuple[faiss.Index, List[Dict[str, str]]]:
        chunks = self._load_chunks()
        if not chunks:
            raise RuntimeError("No chunks found. Run the preprocessor first.")
        vectors = self._encode_chunks(chunk.text for chunk in chunks)
        index = self._build_index(vectors)
        metadata_map = [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "chunk_order": chunk.chunk_order,
            }
            for chunk in chunks
        ]
        self._save_index(index, metadata_map)
        logger.info("FAISS index built with %d vectors", index.ntotal)
        return index, metadata_map

    def _save_index(self, index: faiss.Index, metadata_map: List[Dict[str, str]]) -> None:
        index_path = Path(self.embedding_cfg.index_path)
        metadata_path = Path(self.embedding_cfg.metadata_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(index_path))
        metadata_path.write_text(json.dumps(metadata_map, ensure_ascii=False, indent=2), encoding="utf-8")


def load_faiss_index(index_path: str | Path, metadata_path: str | Path, model_name: str) -> Tuple[faiss.Index, List[Dict[str, str]], SentenceTransformer]:
    index = faiss.read_index(str(index_path))
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    encoder = SentenceTransformer(model_name)
    return index, metadata, encoder


def retrieve_documents(
    query: str,
    index: faiss.Index,
    metadata_map: List[Dict[str, str]],
    encoder: SentenceTransformer,
    top_k: int = 5,
) -> List[Dict[str, str]]:
    query_vec = encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    scores, indices = index.search(query_vec, top_k)
    results: List[Dict[str, str]] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        entry = metadata_map[idx]
        results.append(
            {
                "chunk_id": entry["chunk_id"],
                "text": entry["text"],
                "metadata": entry["metadata"],
                "chunk_order": entry["chunk_order"],
                "similarity_score": float(score),
            }
        )
    return results


__all__ = ["EmbeddingGenerator", "ChunkRecord", "load_faiss_index", "retrieve_documents"]

