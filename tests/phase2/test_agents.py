"""
Quick smoke test for Phase 2 agents.
Run this to verify everything works before using the API.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.phase2_agents.agents import ClauseExtractor, RiskAnalyzer, ComplianceChecker, Summarizer, QAAgent
from src.phase2_agents.orchestration import get_orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample contract text for testing
SAMPLE_CONTRACT = """
AGREEMENT FOR SERVICES

This Agreement is entered into between Company ABC ("Client") and Service Provider XYZ ("Provider") on January 1, 2024.

1. TERMINATION: Either party may terminate this agreement with 30 days written notice.

2. ARBITRATION: Any disputes arising from this agreement shall be resolved through binding arbitration in accordance with the Arbitration and Conciliation Act, 1996.

3. LIABILITY: The Provider's liability shall be limited to the total fees paid under this agreement.

4. CONFIDENTIALITY: Both parties agree to maintain confidentiality of all proprietary information shared during the term of this agreement.

5. PAYMENT: Client shall pay Provider $10,000 within 30 days of service completion.
"""


def test_clause_extractor():
    """Test clause extractor."""
    logger.info("Testing Clause Extractor...")
    extractor = ClauseExtractor()
    clauses = extractor.extract(SAMPLE_CONTRACT)
    logger.info(f"✓ Extracted {len(clauses)} clauses")
    for clause in clauses[:3]:
        logger.info(f"  - {clause.get('clause_type')}: {clause.get('clause_text', '')[:50]}...")
    return len(clauses) > 0


def test_risk_analyzer():
    """Test risk analyzer."""
    logger.info("Testing Risk Analyzer...")
    analyzer = RiskAnalyzer()
    result = analyzer.analyze("Termination clause with 30 days notice", "termination")
    logger.info(f"✓ Risk level: {result.get('risk_level')}")
    return result.get("risk_level") in ["low", "medium", "high"]


def test_compliance_checker():
    """Test compliance checker."""
    logger.info("Testing Compliance Checker...")
    checker = ComplianceChecker()
    result = checker.check("Arbitration clause", "arbitration")
    logger.info(f"✓ Compliance status: {result.get('compliance_status')}")
    return result.get("compliance_status") in ["compliant", "non-compliant", "requires_review"]


def test_summarizer():
    """Test summarizer."""
    logger.info("Testing Summarizer...")
    summarizer = Summarizer()
    result = summarizer.summarize(SAMPLE_CONTRACT)
    logger.info(f"✓ Summary generated: {len(result.get('summary', ''))} chars")
    return result.get("summary") is not None


def test_qa_agent():
    """Test Q&A agent."""
    logger.info("Testing Q&A Agent...")
    qa = QAAgent()
    result = qa.answer("What is the Indian Contract Act?")
    logger.info(f"✓ Answer generated: {len(result.get('answer', ''))} chars")
    return result.get("answer") is not None


def test_orchestrator():
    """Test full orchestrator."""
    logger.info("Testing Orchestrator...")
    orch = get_orchestrator()
    result = orch.analyze_document(
        SAMPLE_CONTRACT,
        extract_clauses=True,
        analyze_risks=True,
        check_compliance=True,
        generate_summary=True,
    )
    logger.info(f"✓ Full analysis complete")
    logger.info(f"  - Clauses: {len(result.get('clauses', []))}")
    logger.info(f"  - Summary: {result.get('summary') is not None}")
    return result.get("clauses") is not None


def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("Phase 2 Agent Smoke Tests")
    logger.info("=" * 50)

    tests = [
        ("Clause Extractor", test_clause_extractor),
        ("Risk Analyzer", test_risk_analyzer),
        ("Compliance Checker", test_compliance_checker),
        ("Summarizer", test_summarizer),
        ("Q&A Agent", test_qa_agent),
        ("Orchestrator", test_orchestrator),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")
            results.append((name, False, str(e)))

    logger.info("=" * 50)
    logger.info("Test Results:")
    logger.info("=" * 50)
    for name, passed, error in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {name}")
        if error:
            logger.info(f"  Error: {error}")

    passed_count = sum(1 for _, passed, _ in results if passed)
    logger.info(f"\n{passed_count}/{len(results)} tests passed")

    return all(passed for _, passed, _ in results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

