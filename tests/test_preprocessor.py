from pathlib import Path

from src.phase1_preprocessing.config import load_config
from src.phase1_preprocessing.preprocessor import Preprocessor, chunk_sentences, clean_text


def test_clean_text_removes_noise():
    text = "Hello!!\n\nWorld\t—   123"
    cleaned = clean_text(text)
    assert cleaned == "Hello!! World 123"


def test_chunk_sentences_overlap():
    sentences = [f"Sentence {i}" for i in range(10)]
    chunks = chunk_sentences(sentences, chunk_size=4, chunk_overlap=2)
    assert len(chunks) >= 3
    # Ensure overlap (last sentence of chunk n equals first of n+1 minus new ones)
    for i in range(len(chunks) - 1):
        overlap = set(" ".join(chunks[i]).split()[-2:])
        next_start = set(" ".join(chunks[i + 1]).split()[:2])
        assert overlap & next_start


def test_process_document_creates_chunks(tmp_path):
    config = load_config()
    sample_text = "This is sentence one. This is sentence two. This is sentence three."
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text(sample_text, encoding="utf-8")
    preprocessor = Preprocessor(config)
    chunks = preprocessor.process_document(sample_file, {"document_type": "test", "title": "Sample"})
    assert chunks, "Expected at least one chunk"
    assert chunks[0].chunk_id.startswith("sample")

