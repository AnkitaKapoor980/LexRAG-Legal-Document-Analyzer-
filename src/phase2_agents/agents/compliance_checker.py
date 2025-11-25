"""
Compliance Checker Agent - Verifies clauses against Indian legal corpus.
"""

import json
import logging
import re
from typing import Dict, Any, List

from ..llm_client import get_llm_client
from ..retriever import get_retriever
from ..prompts.templates import COMPLIANCE_CHECKER_PROMPT

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Checks clause compliance against Indian legal corpus using RAG."""

    def __init__(self, top_k: int = 5):
        """
        Initialize Compliance Checker.

        Args:
            top_k: Number of legal context chunks to retrieve
        """
        self.llm = get_llm_client()
        self.retriever = get_retriever(top_k=top_k)

    def check(self, clause_text: str, clause_type: str = "unknown") -> Dict[str, Any]:
        """
        Check clause compliance against Indian legal corpus.

        Args:
            clause_text: The clause to check
            clause_type: Type of clause

        Returns:
            Compliance check result with status, violations, and citations
        """
        if not clause_text or not clause_text.strip():
            return {
                "compliance_status": "compliant",
                "violations": [],
                "relevant_acts": [],
                "citations": [],
                "explanation": "Empty clause",
            }

        # Retrieve relevant legal context
        query = f"{clause_type} {clause_text[:200]}"
        legal_context_results = self.retriever.retrieve(query, top_k=self.retriever.top_k)
        legal_context = self.retriever.format_context(legal_context_results, max_length=2000)

        # Use LLM to analyze compliance
        try:
            result = self._check_with_llm(clause_text, clause_type, legal_context)
            # Add citations from retrieved chunks
            citations = self.retriever.get_citations(legal_context_results)
            result["citations"] = citations
            return result
        except Exception as e:
            logger.warning(f"LLM compliance check failed: {e}")
            return self._check_with_heuristic(clause_text, legal_context_results)

    def check_batch(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check multiple clauses for compliance.

        Args:
            clauses: List of clause dicts

        Returns:
            List of clauses with added 'compliance_check' field
        """
        results = []
        total = len(clauses)
        for i, clause in enumerate(clauses, 1):
            logger.info(f"  Checking compliance for clause {i}/{total}...")
            clause_text = clause.get("clause_text", "")
            clause_type = clause.get("clause_type", "unknown")
            compliance_check = self.check(clause_text, clause_type)

            result = clause.copy()
            result["compliance_check"] = compliance_check
            results.append(result)

        return results

    def _check_with_llm(
        self, clause_text: str, clause_type: str, legal_context: str
    ) -> Dict[str, Any]:
        """Check compliance using LLM with RAG context."""
        # Truncate if too long
        if len(clause_text) > 2000:
            clause_text = clause_text[:2000] + "... [truncated]"

        prompt = COMPLIANCE_CHECKER_PROMPT.format(
            clause_text=clause_text,
            legal_context=legal_context or "No relevant legal context found.",
        )

        response = self.llm.invoke(prompt)

        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = json.loads(response)

            # Validate compliance status
            status = result.get("compliance_status", "requires_review").lower()
            if status not in ["compliant", "non-compliant", "requires_review"]:
                status = "requires_review"

            return {
                "compliance_status": status,
                "violations": result.get("violations", []),
                "relevant_acts": result.get("relevant_acts", []),
                "citations": result.get("citations", []),
                "explanation": result.get("explanation", "Compliance check completed"),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response[:200]}")
            return {
                "compliance_status": "requires_review",
                "violations": [],
                "relevant_acts": [],
                "citations": [],
                "explanation": "Unable to complete detailed compliance analysis",
            }

    def _check_with_heuristic(
        self, clause_text: str, legal_context_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback heuristic compliance check."""
        citations = self.retriever.get_citations(legal_context_results)
        return {
            "compliance_status": "requires_review",
            "violations": [],
            "relevant_acts": [],
            "citations": citations,
            "explanation": "Heuristic-based check (detailed analysis unavailable)",
        }

