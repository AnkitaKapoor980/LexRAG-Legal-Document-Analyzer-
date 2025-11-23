from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import pdfplumber
import pytesseract
from bs4 import BeautifulSoup
try:
    from pdf2image import convert_from_path
except ImportError:  # pragma: no cover - optional dependency at runtime
    convert_from_path = None  # type: ignore

import spacy
from spacy.language import Language
from spacy.tokens import Doc
from tqdm import tqdm

from .config import AppConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessedChunk:
    chunk_id: str
    text: str
    chunk_order: int
    document_id: str
    metadata: Dict[str, str]


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E]+", " ", text)
    return text.strip()


def chunk_sentences(sentences: Sequence[str], chunk_size: int, chunk_overlap: int) -> List[List[str]]:
    chunks: List[List[str]] = []
    current: List[str] = []
    token_count = 0
    for sentence in sentences:
        sentence_tokens = sentence.split()
        if token_count + len(sentence_tokens) > chunk_size and current:
            chunks.append(current.copy())
            overlap_tokens = " ".join(" ".join(current).split()[-chunk_overlap:])
            current = overlap_tokens.split() if overlap_tokens else []
            token_count = len(current)
        current.append(sentence)
        token_count += len(sentence_tokens)
    if current:
        chunks.append(current)
    return chunks


class Preprocessor:
    """Handles OCR, cleaning, sentence segmentation, and chunking."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.paths = config.paths
        self.preprocessing = config.preprocessing
        self.nlp: Language = self._load_spacy_model(self.preprocessing.spacy_model)
        if config.ocr.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.ocr.tesseract_cmd

    @staticmethod
    def _load_spacy_model(model_name: str) -> Language:
        try:
            return spacy.load(model_name)
        except OSError:
            logger.warning("spaCy model %s not found. Falling back to blank 'en'.", model_name)
            return spacy.blank("en")

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        text_content = []
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    text_content.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover - depends on pdfplumber internals
            logger.error("Failed to parse PDF %s: %s", pdf_path, exc)
        return "\n".join(text_content).strip()

    def _perform_ocr(self, pdf_path: Path) -> str:
        if not convert_from_path:
            logger.warning("pdf2image not installed; cannot OCR %s", pdf_path)
            return ""
        try:
            images = convert_from_path(str(pdf_path), dpi=self.config.ocr.dpi)
        except Exception as exc:  # pragma: no cover - depends on poppler availability
            logger.error("Failed to convert PDF to images for OCR: %s", exc)
            return ""

        ocr_text = []
        for image in images:
            text = pytesseract.image_to_string(image, lang=self.config.ocr.language)
            ocr_text.append(text)
        return "\n".join(ocr_text)

    def _extract_text_from_html(self, html_path: Path) -> str:
        html_content = html_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=" ")

    def _read_document(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text = self._extract_text_from_pdf(path)
            if not text:
                text = self._perform_ocr(path)
            return text
        if suffix in {".html", ".htm"}:
            return self._extract_text_from_html(path)
        return path.read_text(encoding="utf-8", errors="ignore")

    def _tokenize_sentences(self, text: str) -> List[str]:
        doc: Doc = self.nlp(text)
        if doc.has_annotation("SENT_START"):
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        # Fallback if sentence boundary detection missing
        return [s.strip() for s in text.split(". ") if s.strip()]

    def process_document(self, path: Path, metadata: Optional[Dict[str, str]] = None) -> List[ProcessedChunk]:
        raw_text = self._read_document(path)
        if not raw_text:
            logger.warning("Empty document: %s", path)
            return []
        cleaned = clean_text(raw_text)
        max_len = self.preprocessing.max_document_length
        if max_len and len(cleaned) > max_len:
            cleaned = cleaned[:max_len]
        sentences = self._tokenize_sentences(cleaned)
        sentence_chunks = chunk_sentences(
            sentences, self.preprocessing.chunk_size, self.preprocessing.chunk_overlap
        )
        doc_id = path.stem
        processed_chunks: List[ProcessedChunk] = []
        for idx, chunk in enumerate(sentence_chunks, start=1):
            text_chunk = " ".join(chunk).strip()
            if not text_chunk:
                continue
            chunk_id = f"{doc_id}_chunk_{idx:04d}"
            chunk_metadata = {
                "source_path": str(path),
                "document_type": metadata.get("document_type") if metadata else "",
                "title": metadata.get("title") if metadata else doc_id,
                "section": metadata.get("section", ""),
                "year": str(metadata.get("year", "")),
            }
            processed_chunks.append(
                ProcessedChunk(
                    chunk_id=chunk_id,
                    text=text_chunk,
                    chunk_order=idx,
                    document_id=doc_id,
                    metadata=chunk_metadata,
                )
            )
        return processed_chunks

    def _write_chunks(self, doc_id: str, chunks: Iterable[ProcessedChunk]) -> None:
        chunks_path = self.paths.processed_text_dir / f"{doc_id}.jsonl"
        with chunks_path.open("w", encoding="utf-8") as handle:
            for chunk in chunks:
                handle.write(
                    json.dumps(
                        {
                            "chunk_id": chunk.chunk_id,
                            "text": chunk.text,
                            "chunk_order": chunk.chunk_order,
                            "document_id": chunk.document_id,
                            "metadata": chunk.metadata,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    def run(self) -> Dict[str, int]:
        processed_counts: Dict[str, int] = {}
        metadata_files = list(self.paths.metadata_dir.glob("*.json"))
        for meta_file in tqdm(metadata_files, desc="Preprocessing documents"):
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
            doc_path = Path(metadata["local_path"])
            chunks = self.process_document(doc_path, metadata)
            self._write_chunks(metadata["document_id"], chunks)
            metadata["chunk_count"] = len(chunks)
            (self.paths.metadata_dir / f"{metadata['document_id']}.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            processed_counts[metadata["document_id"]] = len(chunks)
        logger.info("Preprocessed %d documents", len(processed_counts))
        return processed_counts


__all__ = ["Preprocessor", "ProcessedChunk", "clean_text", "chunk_sentences"]

