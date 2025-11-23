"""
Phase 1 preprocessing package for LexRAG.

Exposes high-level helpers used by later phases.
"""

from .config import load_config
from .data_collector import DataCollector
from .preprocessor import Preprocessor
from .embedder import EmbeddingGenerator, load_faiss_index, retrieve_documents

__all__ = [
    "load_config",
    "DataCollector",
    "Preprocessor",
    "EmbeddingGenerator",
    "load_faiss_index",
    "retrieve_documents",
]

