"""
Summarizer Agent - Generates plain-language contract summaries.
"""

import json
import logging
import re
from typing import Dict, Any

from ..llm_client import get_llm_client
from ..retriever import get_retriever
from ..prompts.templates import SUMMARIZATION_PROMPT

logger = logging.getLogger(__name__)


class Summarizer:
    """Generates summaries of legal documents using RAG."""

    def __init__(self, top_k: int = 5):
        """
        Initialize Summarizer.

        Args:
            top_k: Number of legal context chunks to retrieve
        """
        self.llm = get_llm_client(purpose="summary")
        self.retriever = get_retriever(top_k=top_k)

    def summarize(self, contract_text: str, query: str = "contract summary") -> Dict[str, Any]:
        """
        Generate a summary of the contract.

        Args:
            contract_text: The contract text to summarize
            query: Optional query to focus the summary

        Returns:
            Summary with key information extracted
        """
        if not contract_text or not contract_text.strip():
            return {
                "summary": "No contract text provided.",
                "key_parties": [],
                "main_obligations": [],
                "key_terms": [],
                "risk_factors": [],
                "important_dates": [],
            }

        # Retrieve relevant legal context for better understanding
        legal_context_results = self.retriever.retrieve(query, top_k=self.retriever.top_k)
        legal_context = self.retriever.format_context(legal_context_results, max_length=1500)

        # Truncate contract text if too long
        max_contract_length = 6000
        if len(contract_text) > max_contract_length:
            contract_text = contract_text[:max_contract_length] + "\n[... text truncated ...]"

        # Use LLM to generate summary
        try:
            return self._summarize_with_llm(contract_text, legal_context)
        except Exception as e:
            logger.warning(f"LLM summarization failed: {e}")
            return self._summarize_with_heuristic(contract_text)

    def _summarize_with_llm(self, contract_text: str, legal_context: str) -> Dict[str, Any]:
        """Generate summary using LLM with RAG context."""
        prompt = SUMMARIZATION_PROMPT.format(
            contract_text=contract_text,
            legal_context=legal_context or "No additional legal context available.",
        )

        response = self.llm.invoke(prompt)

        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = json.loads(response)

            # Validate and set defaults
            return {
                "summary": result.get("summary", "Summary generation completed."),
                "key_parties": result.get("key_parties", []),
                "main_obligations": result.get("main_obligations", []),
                "key_terms": result.get("key_terms", []),
                "risk_factors": result.get("risk_factors", []),
                "important_dates": result.get("important_dates", []),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response[:200]}")
            return {
                "summary": "Unable to generate detailed summary. Please review the contract manually.",
                "key_parties": [],
                "main_obligations": [],
                "key_terms": [],
                "risk_factors": [],
                "important_dates": [],
            }

    def _summarize_with_heuristic(self, contract_text: str) -> Dict[str, Any]:
        """Fallback heuristic summary."""
        # Extract basic info using simple patterns
        parties = []
        obligations = []

        # Try to find party names (simple pattern)
        party_pattern = r"(?:party|parties|between)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        party_matches = re.findall(party_pattern, contract_text[:1000], re.IGNORECASE)
        parties = list(set(party_matches[:5]))  # Limit to 5

        return {
            "summary": f"Contract summary (heuristic): {len(contract_text)} characters. "
                      f"Please review manually for detailed analysis.",
            "key_parties": parties,
            "main_obligations": obligations,
            "key_terms": [],
            "risk_factors": ["Detailed risk analysis unavailable"],
            "important_dates": [],
        }

