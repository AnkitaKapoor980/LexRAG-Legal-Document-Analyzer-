"""
Combined Analyzer Agent - Batch processes all clauses in one LLM call.

This agent combines risk analysis and compliance checking into a single
LLM call to reduce API usage from 2N calls to 1 call for N clauses.
"""

import logging
import json
from typing import Dict, Any, List, Optional

from ..llm_client import get_llm_client
from ..prompts.templates import COMBINED_BATCH_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class CombinedAnalyzer:
    """Analyzes all clauses for risk and compliance in a single batch LLM call."""

    def __init__(self):
        """Initialize the combined analyzer with LLM client."""
        self.llm = get_llm_client(purpose="analysis")

    def analyze_batch(
        self,
        clauses: List[Dict[str, Any]],
        analyze_risks: bool = True,
        check_compliance: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple clauses in a single LLM call.

        Args:
            clauses: List of clause dicts with 'clause_text' and 'clause_type'
            analyze_risks: Whether to include risk analysis
            check_compliance: Whether to include compliance checking

        Returns:
            List of clauses with added 'risk_analysis' and/or 'compliance_check' fields
        """
        if not clauses:
            return []

        if not analyze_risks and not check_compliance:
            return clauses

        logger.info(f"Batch analyzing {len(clauses)} clauses (risk={analyze_risks}, compliance={check_compliance})")

        try:
            # Build the batch prompt
            prompt = self._build_batch_prompt(clauses, analyze_risks, check_compliance)

            # Make single LLM call
            response = self.llm.invoke(prompt)

            # Parse the response
            analyses = self._parse_batch_response(response, len(clauses))

            # Merge analyses with original clauses
            result = self._merge_results(clauses, analyses, analyze_risks, check_compliance)

            logger.info(f"✓ Batch analysis complete for {len(clauses)} clauses")
            return result

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            logger.warning("Falling back to individual analysis")
            return self._fallback_individual_analysis(clauses, analyze_risks, check_compliance)

    def _build_batch_prompt(
        self,
        clauses: List[Dict[str, Any]],
        analyze_risks: bool,
        check_compliance: bool,
    ) -> str:
        """Build the prompt for batch analysis."""
        # Format clauses for the prompt
        clauses_text = ""
        for i, clause in enumerate(clauses):
            clause_type = clause.get("clause_type", "unknown")
            clause_text = clause.get("clause_text", "")
            clauses_text += f"\n{i}. [{clause_type.upper()}]\n{clause_text}\n"

        # Determine what to analyze
        analysis_tasks = []
        if analyze_risks:
            analysis_tasks.append("- Risk level (low/medium/high) and explanation")
        if check_compliance:
            analysis_tasks.append("- Compliance status (compliant/non-compliant/requires_review) and explanation")

        tasks_text = "\n".join(analysis_tasks)

        # Build the prompt
        prompt = f"""You are a legal document analyzer. Analyze the following contract clauses.

For EACH clause, provide:
{tasks_text}

CLAUSES TO ANALYZE:
{clauses_text}

IMPORTANT: Return a valid JSON array with exactly {len(clauses)} objects, one per clause in the EXACT same order.

Example format:
[
  {{
    "clause_index": 0,
    {'"risk_level": "medium",' if analyze_risks else ''}
    {'"risk_explanation": "...",' if analyze_risks else ''}
    {'"compliance_status": "compliant",' if check_compliance else ''}
    {'"compliance_explanation": "..."' if check_compliance else ''}
  }},
  ...
]

Return ONLY the JSON array, no other text.
"""
        return prompt

    def _parse_batch_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse the LLM response into structured data."""
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Find JSON array in response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")
            
            json_text = response_text[start_idx:end_idx]
            analyses = json.loads(json_text)

            if not isinstance(analyses, list):
                raise ValueError("Response is not a JSON array")

            if len(analyses) != expected_count:
                logger.warning(f"Expected {expected_count} analyses, got {len(analyses)}")

            return analyses

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response[:500]}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")

    def _merge_results(
        self,
        clauses: List[Dict[str, Any]],
        analyses: List[Dict[str, Any]],
        analyze_risks: bool,
        check_compliance: bool,
    ) -> List[Dict[str, Any]]:
        """Merge analysis results with original clauses."""
        results = []

        for i, clause in enumerate(clauses):
            result = clause.copy()

            # Get corresponding analysis (if available)
            if i < len(analyses):
                analysis = analyses[i]

                # Add risk analysis
                if analyze_risks:
                    result["risk_analysis"] = {
                        "risk_level": analysis.get("risk_level", "medium"),
                        "explanation": analysis.get("risk_explanation", "No explanation provided"),
                        "factors": [],
                        "mitigation": "Review with legal counsel",
                    }

                # Add compliance check
                if check_compliance:
                    result["compliance_check"] = {
                        "compliance_status": analysis.get("compliance_status", "requires_review"),
                        "explanation": analysis.get("compliance_explanation", "No explanation provided"),
                        "regulations": [],
                        "recommendations": [],
                    }
            else:
                logger.warning(f"No analysis found for clause {i}")

            results.append(result)

        return results

    def _fallback_individual_analysis(
        self,
        clauses: List[Dict[str, Any]],
        analyze_risks: bool,
        check_compliance: bool,
    ) -> List[Dict[str, Any]]:
        """Fallback to individual analysis if batch fails."""
        from .risk_analyzer import RiskAnalyzer
        from .compliance_checker import ComplianceChecker

        results = clauses.copy()

        if analyze_risks:
            logger.info("Falling back to individual risk analysis")
            risk_analyzer = RiskAnalyzer()
            results = risk_analyzer.analyze_batch(results)

        if check_compliance:
            logger.info("Falling back to individual compliance checking")
            compliance_checker = ComplianceChecker()
            results = compliance_checker.check_batch(results)

        return results
