from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class PathsConfig:
    root_dir: Path
    raw_acts_dir: Path
    raw_cases_dir: Path
    raw_contracts_dir: Path
    processed_text_dir: Path
    metadata_dir: Path
    embeddings_dir: Path
    logs_dir: Path


@dataclass
class DataSourcesConfig:
    india_code_acts: List[Dict[str, str]] = field(default_factory=list)
    india_code_min_documents: int = 0
    indian_kanoon_queries: List[str] = field(default_factory=list)
    indian_kanoon_min_documents: int = 0
    cuad_dataset_urls: List[str] = field(default_factory=list)
    cuad_min_documents: int = 0


@dataclass
class PreprocessingConfig:
    chunk_size: int
    chunk_overlap: int
    spacy_model: str
    lowercase_for_embeddings: bool
    preserve_original: bool
    max_document_length: int


@dataclass
class EmbeddingConfig:
    model_name: str
    faiss_index_type: str
    normalize_embeddings: bool
    index_path: Path
    metadata_path: Path


@dataclass
class RateLimitConfig:
    requests_per_minute: int
    max_retries: int
    backoff_factor: float
    timeout_seconds: int


@dataclass
class OCRConfig:
    language: str
    tesseract_cmd: Optional[str]
    dpi: int


@dataclass
class PipelineConfig:
    skip_data_collection_if_exists: bool
    skip_preprocessing_if_exists: bool
    skip_embedding_if_exists: bool


@dataclass
class AppConfig:
    paths: PathsConfig
    data_sources: DataSourcesConfig
    preprocessing: PreprocessingConfig
    embedding: EmbeddingConfig
    rate_limit: RateLimitConfig
    ocr: OCRConfig
    pipeline: PipelineConfig


def _expand_path(base: Path, relative_path: str) -> Path:
    path = Path(relative_path)
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def load_config(config_path: str | Path = "config.yaml") -> AppConfig:
    """Load configuration values from a YAML file."""
    path = Path(config_path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        raw: Dict[str, Any] = yaml.safe_load(handle)

    root_dir = Path(raw["paths"]["root_dir"]).resolve()
    paths = PathsConfig(
        root_dir=root_dir,
        raw_acts_dir=_expand_path(root_dir, raw["paths"]["raw_acts_dir"]),
        raw_cases_dir=_expand_path(root_dir, raw["paths"]["raw_cases_dir"]),
        raw_contracts_dir=_expand_path(root_dir, raw["paths"]["raw_contracts_dir"]),
        processed_text_dir=_expand_path(root_dir, raw["paths"]["processed_text_dir"]),
        metadata_dir=_expand_path(root_dir, raw["paths"]["metadata_dir"]),
        embeddings_dir=_expand_path(root_dir, raw["paths"]["embeddings_dir"]),
        logs_dir=_expand_path(root_dir, raw["paths"]["logs_dir"]),
    )

    ds_raw = raw.get("data_sources", {})
    data_sources = DataSourcesConfig(
        india_code_acts=ds_raw.get("india_code", {}).get("acts", []),
        india_code_min_documents=ds_raw.get("india_code", {}).get("min_documents", 0),
        indian_kanoon_queries=ds_raw.get("indian_kanoon", {}).get("queries", []),
        indian_kanoon_min_documents=ds_raw.get("indian_kanoon", {}).get("min_documents", 0),
        cuad_dataset_urls=ds_raw.get("cuad", {}).get("dataset_urls", []),
        cuad_min_documents=ds_raw.get("cuad", {}).get("min_documents", 0),
    )

    prep_raw = raw.get("preprocessing", {})
    preprocessing = PreprocessingConfig(
        chunk_size=prep_raw.get("chunk_size", 450),
        chunk_overlap=prep_raw.get("chunk_overlap", 75),
        spacy_model=prep_raw.get("spacy_model", "en_core_web_sm"),
        lowercase_for_embeddings=prep_raw.get("lowercase_for_embeddings", True),
        preserve_original=prep_raw.get("preserve_original", True),
        max_document_length=prep_raw.get("max_document_length", 500000),
    )

    embed_raw = raw.get("embedding", {})
    embedding = EmbeddingConfig(
        model_name=embed_raw.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"),
        faiss_index_type=embed_raw.get("faiss_index_type", "IndexFlatIP"),
        normalize_embeddings=embed_raw.get("normalize_embeddings", True),
        index_path=_expand_path(root_dir, embed_raw.get("index_path", "data/embeddings/faiss_index/lexrag.index")),
        metadata_path=_expand_path(
            root_dir, embed_raw.get("metadata_path", "data/embeddings/faiss_index/metadata_map.json")
        ),
    )

    rl_raw = raw.get("rate_limit", {})
    rate_limit = RateLimitConfig(
        requests_per_minute=rl_raw.get("requests_per_minute", 15),
        max_retries=rl_raw.get("max_retries", 3),
        backoff_factor=float(rl_raw.get("backoff_factor", 2.0)),
        timeout_seconds=rl_raw.get("timeout_seconds", 30),
    )

    ocr_raw = raw.get("ocr", {})
    ocr = OCRConfig(
        language=ocr_raw.get("language", "eng"),
        tesseract_cmd=ocr_raw.get("tesseract_cmd") or None,
        dpi=ocr_raw.get("dpi", 300),
    )

    pipeline_raw = raw.get("pipeline", {})
    pipeline = PipelineConfig(
        skip_data_collection_if_exists=pipeline_raw.get("skip_data_collection_if_exists", True),
        skip_preprocessing_if_exists=pipeline_raw.get("skip_preprocessing_if_exists", False),
        skip_embedding_if_exists=pipeline_raw.get("skip_embedding_if_exists", False),
    )

    for directory in [
        paths.raw_acts_dir,
        paths.raw_cases_dir,
        paths.raw_contracts_dir,
        paths.processed_text_dir,
        paths.metadata_dir,
        paths.embeddings_dir,
        paths.logs_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        paths=paths,
        data_sources=data_sources,
        preprocessing=preprocessing,
        embedding=embedding,
        rate_limit=rate_limit,
        ocr=ocr,
        pipeline=pipeline,
    )


__all__ = [
    "AppConfig",
    "PathsConfig",
    "DataSourcesConfig",
    "PreprocessingConfig",
    "EmbeddingConfig",
    "RateLimitConfig",
    "OCRConfig",
    "PipelineConfig",
    "load_config",
]

