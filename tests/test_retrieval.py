import json
from pathlib import Path

import faiss
import numpy as np

from src.phase1_preprocessing import config as config_module
from src.phase1_preprocessing.embedder import load_faiss_index


class StubEncoder:
    def __init__(self, *args, **kwargs):
        self.model_name = args[0] if args else "stub"

    def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
        return np.ones((len(texts), 2), dtype="float32")


def test_load_faiss_index(monkeypatch, tmp_path):
    monkeypatch.setattr("src.phase1_preprocessing.embedder.SentenceTransformer", StubEncoder)
    index = faiss.IndexFlatIP(2)
    index.add(np.array([[1.0, 0.0]], dtype="float32"))
    index_path = tmp_path / "lexrag.index"
    faiss.write_index(index, str(index_path))
    metadata = [{"chunk_id": "chunk_1", "text": "sample text", "metadata": {}, "chunk_order": 1}]
    metadata_path = tmp_path / "metadata_map.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    loaded_index, loaded_metadata, encoder = load_faiss_index(index_path, metadata_path, "stub-model")
    assert loaded_index.ntotal == 1
    assert loaded_metadata[0]["chunk_id"] == "chunk_1"
    assert isinstance(encoder, StubEncoder)

