"""
Risk Analyzer Agent - Assesses risk levels of contract clauses.
"""

import json
import logging
import re
from typing import Dict, Any, List

from ..llm_client import get_llm_client
from ..prompts.templates import RISK_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Analyzes risk levels of contract clauses."""

    def __init__(self):
        """Initialize Risk Analyzer."""
        self.llm = get_llm_client()

    def analyze(self, clause_text: str, clause_type: str = "unknown") -> Dict[str, Any]:
        """
        Analyze risk level of a clause.

        Args:
            clause_text: The clause text to analyze
            clause_type: Type of clause (e.g., "termination", "liability")

        Returns:
            Risk analysis result with risk_level, explanation, and concerns
        """
        if not clause_text or not clause_text.strip():
            return {
                "risk_level": "low",
                "explanation": "Empty clause",
                "concerns": [],
            }

        # Quick heuristic check for obvious high-risk keywords
        high_risk_keywords = [
            "unlimited liability",
            "no liability",
            "waiver of rights",
            "binding arbitration",
            "exclusive jurisdiction",
            "penalty",
            "forfeiture",
        ]

        clause_lower = clause_text.lower()
        has_high_risk_keywords = any(keyword in clause_lower for keyword in high_risk_keywords)

        # Use LLM for detailed analysis
        try:
            result = self._analyze_with_llm(clause_text, clause_type)
            # Override with heuristic if high-risk keywords found
            if has_high_risk_keywords and result["risk_level"] == "low":
                result["risk_level"] = "medium"
                result["concerns"].append("Contains high-risk legal terms")
            return result
        except Exception as e:
            logger.warning(f"LLM analysis failed, using heuristic: {e}")
            return self._analyze_with_heuristic(clause_text, has_high_risk_keywords)

    def analyze_batch(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple clauses.

        Args:
            clauses: List of clause dicts with 'clause_text' and optionally 'clause_type'

        Returns:
            List of clauses with added 'risk_analysis' field
        """
        results = []
        total = len(clauses)
        for i, clause in enumerate(clauses, 1):
            logger.info(f"  Analyzing risk for clause {i}/{total}...")
            clause_text = clause.get("clause_text", "")
            clause_type = clause.get("clause_type", "unknown")
            risk_analysis = self.analyze(clause_text, clause_type)

            result = clause.copy()
            result["risk_analysis"] = risk_analysis
            results.append(result)

        return results

    def _analyze_with_llm(self, clause_text: str, clause_type: str) -> Dict[str, Any]:
        """Analyze risk using LLM."""
        # Truncate if too long
        if len(clause_text) > 2000:
            clause_text = clause_text[:2000] + "... [truncated]"

        prompt = RISK_ANALYSIS_PROMPT.format(
            clause_text=clause_text,
            clause_type=clause_type,
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
            risk_level = result.get("risk_level", "medium").lower()
            if risk_level not in ["low", "medium", "high"]:
                risk_level = "medium"

            return {
                "risk_level": risk_level,
                "explanation": result.get("explanation", "Risk analysis completed"),
                "concerns": result.get("concerns", []),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response[:200]}")
            return {
                "risk_level": "medium",
                "explanation": "Analysis completed with default assessment",
                "concerns": ["Unable to parse detailed analysis"],
            }

    def _analyze_with_heuristic(self, clause_text: str, has_high_risk: bool) -> Dict[str, Any]:
        """Fallback heuristic risk analysis."""
        risk_level = "high" if has_high_risk else "medium"
        return {
            "risk_level": risk_level,
            "explanation": "Heuristic-based risk assessment",
            "concerns": ["Detailed analysis unavailable"] if has_high_risk else [],
        }

