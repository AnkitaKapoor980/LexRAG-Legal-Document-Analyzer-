"""
Agent Orchestration - Coordinates all agents in a pipeline.
"""

import logging
from typing import Dict, Any, List, Optional

from .agents import (
    ClauseExtractor,
    RiskAnalyzer,
    ComplianceChecker,
    Summarizer,
    QAAgent,
    CombinedAnalyzer,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents to analyze legal documents."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.clause_extractor = ClauseExtractor()
        self.risk_analyzer = RiskAnalyzer()
        self.compliance_checker = ComplianceChecker()
        self.summarizer = Summarizer()
        self.qa_agent = QAAgent()
        self.combined_analyzer = CombinedAnalyzer()  # Batch analyzer

    def analyze_document(
        self,
        contract_text: str,
        extract_clauses: bool = True,
        analyze_risks: bool = True,
        check_compliance: bool = True,
        generate_summary: bool = True,
    ) -> Dict[str, Any]:
        """
        Full document analysis pipeline.

        Args:
            contract_text: The contract text to analyze
            extract_clauses: Whether to extract clauses
            analyze_risks: Whether to analyze risks
            check_compliance: Whether to check compliance
            generate_summary: Whether to generate summary

        Returns:
            Complete analysis result
        """
        logger.info("=" * 60)
        logger.info("Starting document analysis pipeline")
        logger.info(f"Document length: {len(contract_text)} characters")
        logger.info("=" * 60)
        
        result: Dict[str, Any] = {
            "document_length": len(contract_text),
            "clauses": [],
            "summary": None,
            "statistics": {},
        }

        # Step 1: Extract clauses
        if extract_clauses:
            logger.info("Step 1/4: Extracting clauses...")
            import time
            start_time = time.time()
            clauses = self.clause_extractor.extract(contract_text)
            elapsed = time.time() - start_time
            result["clauses"] = clauses
            result["statistics"]["total_clauses"] = len(clauses)
            logger.info(f"✓ Extracted {len(clauses)} clauses in {elapsed:.2f}s")

            # Step 2: Combined batch analysis (risk + compliance in ONE call)
            if (analyze_risks or check_compliance) and clauses:
                logger.info(f"Step 2/4: Batch analyzing {len(clauses)} clauses (risk + compliance)...")
                start_time = time.time()
                
                # Single LLM call for all clauses
                analyzed_clauses = self.combined_analyzer.analyze_batch(
                    clauses,
                    analyze_risks=analyze_risks,
                    check_compliance=check_compliance
                )
                
                elapsed = time.time() - start_time
                result["clauses"] = analyzed_clauses
                logger.info(f"✓ Batch analysis complete in {elapsed:.2f}s (1 LLM call for {len(clauses)} clauses)")

                # Calculate risk statistics
                if analyze_risks:
                    risk_counts = {"low": 0, "medium": 0, "high": 0}
                    for clause in analyzed_clauses:
                        if "risk_analysis" in clause:
                            risk_level = clause["risk_analysis"].get("risk_level", "medium")
                            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
                    result["statistics"]["risk_distribution"] = risk_counts
                    logger.info(f"  Risk distribution: {risk_counts}")

                # Calculate compliance statistics
                if check_compliance:
                    compliance_counts = {"compliant": 0, "non-compliant": 0, "requires_review": 0}
                    for clause in analyzed_clauses:
                        if "compliance_check" in clause:
                            status = clause["compliance_check"].get("compliance_status", "requires_review")
                            compliance_counts[status] = compliance_counts.get(status, 0) + 1
                    result["statistics"]["compliance_distribution"] = compliance_counts
                    logger.info(f"  Compliance distribution: {compliance_counts}")

        # Step 3: Generate summary
        if generate_summary:
            logger.info("Step 3/3: Generating document summary...")
            start_time = time.time()
            summary = self.summarizer.summarize(contract_text)
            elapsed = time.time() - start_time
            result["summary"] = summary
            logger.info(f"✓ Summary generated in {elapsed:.2f}s")

        logger.info("=" * 60)
        logger.info("✅ Document analysis complete!")
        logger.info("=" * 60)
        return result

    def answer_question(self, question: str, clear_history: bool = False) -> Dict[str, Any]:
        """
        Answer a legal question (standalone, not part of document analysis).

        Args:
            question: The question to answer
            clear_history: Whether to clear conversation history

        Returns:
            Answer with sources
        """
        return self.qa_agent.answer(question, clear_history=clear_history)

    def extract_clauses_only(self, contract_text: str) -> List[Dict[str, Any]]:
        """Extract clauses only (no analysis)."""
        return self.clause_extractor.extract(contract_text)

    def analyze_risks_only(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze risks for given clauses only."""
        return self.risk_analyzer.analyze_batch(clauses)

    def check_compliance_only(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check compliance for given clauses only."""
        return self.compliance_checker.check_batch(clauses)

    def summarize_only(self, contract_text: str) -> Dict[str, Any]:
        """Generate summary only."""
        return self.summarizer.summarize(contract_text)


# Global instance
_global_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator instance."""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator()
    return _global_orchestrator

