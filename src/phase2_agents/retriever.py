"""
RAG Retriever wrapper for Phase 1 FAISS index.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.phase1_preprocessing.config import load_config
from src.phase1_preprocessing.embedder import load_faiss_index, retrieve_documents
import faiss

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Wrapper for Phase 1 FAISS retrieval with caching."""

    def __init__(self, top_k: int = 5):
        """
        Initialize RAG retriever.

        Args:
            top_k: Default number of chunks to retrieve
        """
        self.top_k = top_k
        self.config = load_config()
        self.index: Optional[faiss.Index] = None
        self.metadata_map: Optional[List[Dict[str, Any]]] = None
        self.encoder = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of FAISS index."""
        if self._initialized:
            return

        index_path = Path(self.config.embedding.index_path)
        metadata_path = Path(self.config.embedding.metadata_path)

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found. Run Phase 1 pipeline first.\n"
                f"Expected: {index_path}\n"
                f"Expected: {metadata_path}"
            )

        logger.info("Loading FAISS index and metadata...")
        self.index, self.metadata_map, self.encoder = load_faiss_index(
            index_path,
            metadata_path,
            self.config.embedding.model_name,
        )
        self._initialized = True
        logger.info(f"Loaded index with {self.index.ntotal} vectors")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            top_k: Number of results (defaults to self.top_k)

        Returns:
            List of retrieved chunks with metadata
        """
        self._initialize()

        k = top_k if top_k is not None else self.top_k
        results = retrieve_documents(
            query=query,
            index=self.index,
            metadata_map=self.metadata_map,
            encoder=self.encoder,
            top_k=k,
        )

        logger.debug(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
        return results

    def format_context(self, results: List[Dict[str, Any]], max_length: int = 2000) -> str:
        """
        Format retrieved chunks into a context string for LLM prompts.

        Args:
            results: Retrieved chunks from retrieve()
            max_length: Maximum total length of context

        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            chunk_text = result["text"]
            metadata = result.get("metadata", {})
            title = metadata.get("title", "Unknown")
            source = metadata.get("source_path", "Unknown")

            # Format chunk
            chunk_str = f"[Chunk {i}] Source: {title}\n{chunk_text}\n"
            chunk_length = len(chunk_str)

            if current_length + chunk_length > max_length:
                break

            context_parts.append(chunk_str)
            current_length += chunk_length

        return "\n".join(context_parts)

    def get_citations(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract citation information from retrieved chunks.

        Args:
            results: Retrieved chunks

        Returns:
            List of citation dicts with title, source, chunk_id
        """
        citations = []
        for result in results:
            metadata = result.get("metadata", {})
            citations.append({
                "chunk_id": result.get("chunk_id", ""),
                "title": metadata.get("title", "Unknown"),
                "source": metadata.get("source_path", ""),
                "year": metadata.get("year", ""),
                "similarity_score": result.get("similarity_score", 0.0),
            })
        return citations


# Global instance (lazy initialization)
_global_retriever: Optional[RAGRetriever] = None


def get_retriever(top_k: int = 5) -> RAGRetriever:
    """Get or create global retriever instance."""
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = RAGRetriever(top_k=top_k)
    return _global_retriever

