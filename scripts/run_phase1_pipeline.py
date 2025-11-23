from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.phase1_preprocessing import DataCollector, EmbeddingGenerator, Preprocessor, load_config
import os


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "phase1_pipeline.log", encoding="utf-8"),
        ],
    )


def run_pipeline(force_refresh: bool, skip_embeddings: bool) -> None:
    config = load_config()
    setup_logging(config.paths.logs_dir)

    collector = DataCollector(config)
    preprocessor = Preprocessor(config)
    # Embedding model can be overridden via env var EMBEDDING_MODEL or CLI flag.
    embedder = EmbeddingGenerator(config)

    if not (config.paths.raw_acts_dir.exists() and any(config.paths.raw_acts_dir.iterdir())) or not config.pipeline.skip_data_collection_if_exists or force_refresh:
        logging.info("Starting data collection")
        collector.run()
    else:
        logging.info("Skipping data collection (data already present)")

    if not config.pipeline.skip_preprocessing_if_exists or force_refresh:
        logging.info("Starting preprocessing")
        preprocessor.run()
    else:
        logging.info("Skipping preprocessing per configuration")

    if skip_embeddings:
        logging.info("Skipping embedding generation per CLI flag")
        return

    if not config.pipeline.skip_embedding_if_exists or force_refresh or not Path(config.embedding.index_path).exists():
        logging.info("Building FAISS index")
        embedder.build()
    else:
        logging.info("Skipping embedding generation; index already exists")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LexRAG Phase 1 pipeline.")
    parser.add_argument("--force-refresh", action="store_true", help="Re-download and reprocess all data.")
    parser.add_argument("--skip-embeddings", action="store_true", help="Stop after preprocessing.")
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        help="Temporarily override the embedding model (same as setting EMBEDDING_MODEL env var).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # If embedding-model provided via CLI, set env var so EmbeddingGenerator picks it up.
    if args.embedding_model:
        os.environ["EMBEDDING_MODEL"] = args.embedding_model
    run_pipeline(force_refresh=args.force_refresh, skip_embeddings=args.skip_embeddings)

