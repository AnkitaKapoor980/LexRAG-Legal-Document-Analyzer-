import numpy as np
import faiss

from src.phase1_preprocessing.embedder import retrieve_documents


class DummyEncoder:
    def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
        vectors = []
        for text in texts:
            if "contract" in text or "contract" in text.lower():
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        arr = np.array(vectors, dtype="float32")
        if normalize_embeddings:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1
            arr = arr / norms
        return arr


def test_retrieve_documents_orders_by_similarity():
    index = faiss.IndexFlatIP(2)
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
    index.add(vectors)
    metadata_map = [
        {"chunk_id": "chunk_contract", "text": "contract termination clause", "metadata": {}, "chunk_order": 1},
        {"chunk_id": "chunk_penal", "text": "criminal provisions", "metadata": {}, "chunk_order": 1},
    ]
    encoder = DummyEncoder()
    results = retrieve_documents("contract remedies", index, metadata_map, encoder, top_k=2)
    assert results[0]["chunk_id"] == "chunk_contract"

