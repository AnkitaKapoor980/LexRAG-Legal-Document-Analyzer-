"""
Clause Extractor Agent - Identifies and extracts clauses from contracts.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional

from ..llm_client import get_llm_client
from ..prompts.templates import CLAUSE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ClauseExtractor:
    """Extracts clauses from legal documents using LLM and regex."""

    def __init__(self):
        """Initialize the clause extractor with LLM client."""
        self.llm = get_llm_client(purpose="extraction")

    def extract(self, contract_text: str, use_llm: bool = True) -> List[Dict[str, Any]]:
        """
        Extract clauses from contract text.

        Args:
            contract_text: The contract text to analyze
            use_llm: Whether to use LLM (True) or regex only (False)

        Returns:
            List of extracted clauses with metadata
        """
        if not contract_text or not contract_text.strip():
            return []

        # First, try regex-based extraction for common clauses
        regex_clauses = self._extract_with_regex(contract_text)

        if not use_llm:
            return regex_clauses

        # Use LLM for more comprehensive extraction
        try:
            llm_clauses = self._extract_with_llm(contract_text)
            # Merge results, prioritizing LLM results
            return self._merge_clauses(regex_clauses, llm_clauses)
        except Exception as e:
            logger.warning(f"LLM extraction failed, using regex only: {e}")
            return regex_clauses

    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract clauses using regex patterns."""
        clauses = []
        patterns = {
            "termination": [
                r"(?:termination|terminate|end of agreement).{0,1500}",
                r"(?:terminate|termination).{0,500}(?:notice|period|clause).{0,1000}",
            ],
            "arbitration": [
                r"(?:arbitration|arbitrate|arbitral).{0,1500}",
                r"(?:dispute|disagreement).{0,500}(?:arbitration|arbitrate).{0,1000}",
            ],
            "liability": [
                r"(?:liability|liable|indemnify|indemnification).{0,1500}",
                r"(?:limitation of liability|limited liability).{0,1500}",
            ],
            "confidentiality": [
                r"(?:confidential|confidentiality|non-disclosure|NDA).{0,1500}",
            ],
            "payment": [
                r"(?:payment|pay|fee|compensation|remuneration).{0,1500}",
            ],
        }

        for clause_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    clause_text = match.group(0).strip()
                    if len(clause_text) > 20:  # Filter very short matches
                        # Don't truncate - keep full clause text
                        clauses.append({
                            "clause_type": clause_type,
                            "clause_text": clause_text,  # No truncation
                            "start_position": match.start(),
                            "importance": "medium",
                            "extraction_method": "regex",
                        })

        # Remove duplicates (same clause_type and similar text)
        unique_clauses = []
        seen = set()
        for clause in clauses:
            key = (clause["clause_type"], clause["clause_text"][:50])
            if key not in seen:
                seen.add(key)
                unique_clauses.append(clause)

        return unique_clauses[:20]  # Limit to 20 clauses

    def _extract_with_llm(self, text: str) -> List[Dict[str, Any]]:
        """Extract clauses using LLM."""
        # Truncate text if too long (LLM context limits)
        max_length = 4000
        if len(text) > max_length:
            text = text[:max_length] + "\n[... text truncated ...]"

        prompt = CLAUSE_EXTRACTION_PROMPT.format(contract_text=text)
        response = self.llm.invoke(prompt)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                clauses = json.loads(json_match.group(0))
            else:
                clauses = json.loads(response)

            # Validate and clean clauses
            validated_clauses = []
            for clause in clauses:
                if isinstance(clause, dict) and "clause_type" in clause and "clause_text" in clause:
                    validated_clauses.append({
                        "clause_type": clause.get("clause_type", "unknown"),
                        "clause_text": clause.get("clause_text", ""),
                        "start_position": clause.get("start_position", -1),
                        "importance": clause.get("importance", "medium"),
                        "extraction_method": "llm",
                    })

            return validated_clauses
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response[:200]}")
            return []

    def _merge_clauses(self, regex_clauses: List[Dict], llm_clauses: List[Dict]) -> List[Dict]:
        """Merge regex and LLM extracted clauses, removing duplicates."""
        merged = []
        seen_texts = set()

        # Prefer LLM clauses
        for clause in llm_clauses:
            text_snippet = clause["clause_text"][:100].lower()
            if text_snippet not in seen_texts:
                seen_texts.add(text_snippet)
                merged.append(clause)

        # Add regex clauses that don't overlap
        for clause in regex_clauses:
            text_snippet = clause["clause_text"][:100].lower()
            if text_snippet not in seen_texts:
                seen_texts.add(text_snippet)
                merged.append(clause)

        return merged[:30]  # Limit total clauses

