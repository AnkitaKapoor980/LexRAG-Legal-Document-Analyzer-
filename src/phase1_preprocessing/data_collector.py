from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup
from requests import Response, Session
from tqdm import tqdm

from .config import AppConfig

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    ACT = "act"
    CASE = "case"
    CONTRACT = "contract"


@dataclass
class DocumentMetadata:
    document_id: str
    title: str
    source_url: str
    document_type: DocumentType
    downloaded_at: str
    local_path: str
    extra: Dict[str, str]


class DataCollector:
    """Downloads legal documents from India Code, Indian Kanoon, and CUAD."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.session: Session = requests.Session()
        self.request_interval = 60 / max(1, config.rate_limit.requests_per_minute)
        self.last_request_ts = 0.0
        self.failed_urls: List[str] = []
        self._prepare_logging()

    def _prepare_logging(self) -> None:
        log_dir = self.config.paths.logs_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "phase1.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    def _throttle(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_ts
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_ts = time.time()

    def _fetch(self, url: str) -> Optional[Response]:
        """Fetch content with retry/backoff."""
        retries = 0
        while retries <= self.config.rate_limit.max_retries:
            try:
                self._throttle()
                response = self.session.get(url, timeout=self.config.rate_limit.timeout_seconds)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                wait = (self.config.rate_limit.backoff_factor ** retries)
                logger.warning("Request failed (%s). Retrying in %.1fs", exc, wait)
                time.sleep(wait)
                retries += 1
        self.failed_urls.append(url)
        logger.error("Giving up on %s after %d retries", url, retries)
        return None

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", "_", value)
        return value.strip("_")

    def _save_document(self, content: bytes, directory: Path, filename: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / filename
        target.write_bytes(content)
        return target

    def _save_metadata(self, metadata: DocumentMetadata) -> None:
        meta_path = self.config.paths.metadata_dir / f"{metadata.document_id}.json"
        payload = asdict(metadata)
        payload["document_type"] = metadata.document_type.value
        with meta_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def collect_india_code_acts(self) -> List[DocumentMetadata]:
        logger.info("Collecting India Code acts")
        collected: List[DocumentMetadata] = []
        for act in tqdm(self.config.data_sources.india_code_acts, desc="India Code Acts"):
            title = act["title"]
            url = act["url"]
            slug = self._slugify(title)
            filename = f"{slug}.html"
            target_path = self.config.paths.raw_acts_dir / filename
            if target_path.exists():
                logger.info("Skipping existing act: %s", title)
                metadata = DocumentMetadata(
                    document_id=slug,
                    title=title,
                    source_url=url,
                    document_type=DocumentType.ACT,
                    downloaded_at=datetime.utcnow().isoformat(),
                    local_path=str(target_path),
                    extra={"note": "previously downloaded"},
                )
                meta_file = self.config.paths.metadata_dir / f"{slug}.json"
                if not meta_file.exists():
                    self._save_metadata(metadata)
                collected.append(metadata)
                continue

            response = self._fetch(url)
            if not response:
                continue
            saved_path = self._save_document(response.content, self.config.paths.raw_acts_dir, filename)
            metadata = DocumentMetadata(
                document_id=slug,
                title=title,
                source_url=url,
                document_type=DocumentType.ACT,
                downloaded_at=datetime.utcnow().isoformat(),
                local_path=str(saved_path),
                extra={"content_type": response.headers.get("Content-Type", "")},
            )
            self._save_metadata(metadata)
            collected.append(metadata)
        return collected

    def _parse_kanoon_search(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for anchor in soup.select("div.result_title a"):
            href = anchor.get("href")
            if not href:
                continue
            links.append(urljoin("https://indiankanoon.org", href))
        return links

    def collect_indian_kanoon_cases(self, limit: Optional[int] = None) -> List[DocumentMetadata]:
        logger.info("Collecting Indian Kanoon cases")
        collected: List[DocumentMetadata] = []
        desired = limit or self.config.data_sources.indian_kanoon_min_documents
        seen_links: set[str] = set()
        for query in self.config.data_sources.indian_kanoon_queries:
            search_url = f"https://indiankanoon.org/search/?formInput={quote_plus(query)}"
            response = self._fetch(search_url)
            if not response:
                continue
            case_links = self._parse_kanoon_search(response.text)
            for case_url in case_links:
                if case_url in seen_links:
                    continue
                seen_links.add(case_url)
                slug = self._slugify(case_url.split("/")[-2])
                filename = f"{slug}.html"
                target_path = self.config.paths.raw_cases_dir / filename
                if target_path.exists():
                    logger.info("Skipping existing case: %s", case_url)
                    meta_file = self.config.paths.metadata_dir / f"{slug}.json"
                    if not meta_file.exists():
                        existing_metadata = DocumentMetadata(
                            document_id=slug,
                            title=self._extract_case_title(target_path.read_text(encoding="utf-8", errors="ignore"))
                            or slug,
                            source_url=case_url,
                            document_type=DocumentType.CASE,
                            downloaded_at=datetime.utcnow().isoformat(),
                            local_path=str(target_path),
                            extra={"query": query},
                        )
                        self._save_metadata(existing_metadata)
                    continue
                case_response = self._fetch(case_url)
                if not case_response:
                    continue
                saved_path = self._save_document(case_response.content, self.config.paths.raw_cases_dir, filename)
                title = self._extract_case_title(case_response.text) or slug.replace("_", " ").title()
                metadata = DocumentMetadata(
                    document_id=slug,
                    title=title,
                    source_url=case_url,
                    document_type=DocumentType.CASE,
                    downloaded_at=datetime.utcnow().isoformat(),
                    local_path=str(saved_path),
                    extra={"query": query},
                )
                self._save_metadata(metadata)
                collected.append(metadata)
                if len(collected) >= desired:
                    return collected
        return collected

    @staticmethod
    def _extract_case_title(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        h2 = soup.find("h2")
        if h2:
            return h2.get_text(strip=True)
        return None

    def download_cuad_contracts(self) -> List[DocumentMetadata]:
        logger.info("Downloading CUAD contracts")
        collected: List[DocumentMetadata] = []
        for url in self.config.data_sources.cuad_dataset_urls:
            slug = self._slugify(Path(url).stem)
            filename = Path(url).name
            target_path = self.config.paths.raw_contracts_dir / filename
            if target_path.exists():
                logger.info("CUAD file already exists: %s", filename)
            else:
                response = self._fetch(url)
                if not response:
                    continue
                saved_path = self._save_document(response.content, self.config.paths.raw_contracts_dir, filename)
                if filename.endswith(".zip"):
                    self._extract_zip(saved_path, self.config.paths.raw_contracts_dir)
            metadata = DocumentMetadata(
                document_id=slug,
                title=filename,
                source_url=url,
                document_type=DocumentType.CONTRACT,
                downloaded_at=datetime.utcnow().isoformat(),
                local_path=str(target_path),
                extra={},
            )
            self._save_metadata(metadata)
            collected.append(metadata)
        return collected

    @staticmethod
    def _extract_zip(zip_path: Path, destination: Path) -> None:
        try:
            import zipfile
        except ImportError:
            logger.warning("zipfile module unavailable; skipping extraction for %s", zip_path)
            return
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(destination)

    def run(self) -> Dict[str, List[DocumentMetadata]]:
        """Execute the full collection pipeline."""
        results = {
            "acts": self.collect_india_code_acts(),
            "cases": self.collect_indian_kanoon_cases(),
            "contracts": self.download_cuad_contracts(),
            "failed": self.failed_urls,
        }
        logger.info("Collection finished. %d failures.", len(self.failed_urls))
        if self.failed_urls:
            failed_log = self.config.paths.logs_dir / "failed_downloads.txt"
            failed_log.write_text("\n".join(self.failed_urls), encoding="utf-8")
        return results


__all__ = ["DataCollector", "DocumentType", "DocumentMetadata"]

