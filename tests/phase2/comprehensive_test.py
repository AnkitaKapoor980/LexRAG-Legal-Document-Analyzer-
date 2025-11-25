"""
Comprehensive test suite for Phase 2 agents with real contract example.
Generates detailed test report.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
import sys

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.phase2_agents.agents import ClauseExtractor, RiskAnalyzer, ComplianceChecker, Summarizer, QAAgent
from src.phase2_agents.orchestration import get_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# Real-world contract example (Indian contract template)
REAL_CONTRACT = """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on [Date], between:

Party A: ABC Technologies Private Limited, a company incorporated under the Companies Act, 2013, 
having its registered office at 123 Tech Park, Bangalore, Karnataka, India ("Service Provider")

Party B: XYZ Solutions Pvt. Ltd., a company incorporated under the Companies Act, 2013,
having its registered office at 456 Business Tower, Mumbai, Maharashtra, India ("Client")

WHEREAS:
The Service Provider is engaged in providing software development and consulting services;
The Client desires to engage the Service Provider for software development services;
Both parties wish to set forth the terms and conditions governing such services.

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

1. TERM AND TERMINATION

1.1 This Agreement shall commence on [Start Date] and shall continue for a period of 12 months ("Initial Term").

1.2 Either party may terminate this Agreement by giving 30 days written notice to the other party.

1.3 The Service Provider may terminate this Agreement immediately in case of non-payment by Client beyond 60 days of invoice date.

1.4 Upon termination, all outstanding invoices shall become immediately due and payable.

2. SERVICES AND DELIVERABLES

2.1 The Service Provider shall provide software development services as specified in the Statement of Work attached as Schedule A.

2.2 All deliverables shall be provided in accordance with industry best practices and standards.

2.3 The Client shall have 15 days from delivery to provide feedback or request modifications.

3. COMPENSATION AND PAYMENT

3.1 The Client agrees to pay the Service Provider a total fee of INR 50,00,000 (Fifty Lakhs) for the services rendered.

3.2 Payment shall be made as follows:
    - 30% upon signing this Agreement
    - 40% upon completion of Phase 1
    - 30% upon final delivery and acceptance

3.3 All payments shall be made within 30 days of invoice date.

3.4 Interest at the rate of 18% per annum shall be charged on overdue payments.

4. INTELLECTUAL PROPERTY RIGHTS

4.1 All intellectual property rights in the deliverables shall vest with the Client upon full payment.

4.2 The Service Provider retains rights to any pre-existing intellectual property used in the deliverables.

5. CONFIDENTIALITY

5.1 Both parties agree to maintain confidentiality of all proprietary information shared during the term of this Agreement.

5.2 Confidential information includes but is not limited to business plans, technical specifications, financial information, and client data.

5.3 The confidentiality obligations shall survive termination of this Agreement for a period of 3 years.

6. LIABILITY AND INDEMNIFICATION

6.1 The Service Provider's liability shall be limited to the total fees received under this Agreement.

6.2 Neither party shall be liable for indirect, incidental, or consequential damages.

6.3 Each party shall indemnify the other against claims arising from breach of this Agreement.

7. DISPUTE RESOLUTION

7.1 Any disputes arising out of or in connection with this Agreement shall be resolved through arbitration in accordance with the Arbitration and Conciliation Act, 2015.

7.2 The arbitration shall be conducted in English language in Bangalore, India.

7.3 The arbitration award shall be final and binding on both parties.

8. GOVERNING LAW

8.1 This Agreement shall be governed by and construed in accordance with the laws of India.

8.2 Any disputes shall be subject to the exclusive jurisdiction of courts in Bangalore, India.

9. FORCE MAJEURE

9.1 Neither party shall be liable for failure to perform due to circumstances beyond their reasonable control.

10. MISCELLANEOUS

10.1 This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements.

10.2 No modification shall be valid unless in writing and signed by both parties.

10.3 If any provision is found to be invalid, the remaining provisions shall remain in full force.

IN WITNESS WHEREOF, the parties have executed this Agreement on the date first written above.

Service Provider:                    Client:
___________________                  ___________________
Authorized Signatory                 Authorized Signatory
"""


class TestReport:
    """Generate comprehensive test report."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = []
        self.errors = []
        self.summary = {}
        
    def add_result(self, test_name: str, passed: bool, details: dict, error: str = None):
        """Add a test result."""
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        if not passed:
            self.errors.append(f"{test_name}: {error}")
    
    def generate_report(self) -> dict:
        """Generate full test report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed_count = sum(1 for r in self.results if r["passed"])
        total_count = len(self.results)
        
        self.summary = {
            "test_date": self.start_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "success_rate": f"{(passed_count/total_count*100):.1f}%" if total_count > 0 else "0%",
            "status": "PASS" if passed_count == total_count else "FAIL"
        }
        
        return {
            "summary": self.summary,
            "results": self.results,
            "errors": self.errors
        }
    
    def print_report(self):
        """Print formatted report."""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("PHASE 2 COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Test Date: {report['summary']['test_date']}")
        print(f"Duration: {report['summary']['duration_seconds']:.2f} seconds")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['success_rate']}")
        print(f"Status: {report['summary']['status']}")
        print("="*80)
        
        print("\nDETAILED RESULTS:")
        print("-"*80)
        for result in report['results']:
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"\n{status}: {result['test_name']}")
            if result['details']:
                print(f"  Details: {json.dumps(result['details'], indent=4, default=str)}")
            if result['error']:
                print(f"  Error: {result['error']}")
        
        if report['errors']:
            print("\n" + "="*80)
            print("ERRORS:")
            print("-"*80)
            for error in report['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*80)
        
        return report


def run_clause_extractor(report: TestReport) -> list:
    """Run clause extractor with real contract."""
    logger.info("="*60)
    logger.info("TEST 1: Clause Extractor")
    logger.info("="*60)
    
    try:
        extractor = ClauseExtractor()
        clauses = extractor.extract(REAL_CONTRACT)
        
        # Check results
        details = {
            "total_clauses_extracted": len(clauses),
            "clause_types_found": list(set(c.get("clause_type") for c in clauses)),
            "sample_clauses": [
                {
                    "type": c.get("clause_type"),
                    "text_preview": c.get("clause_text", "")[:100] + "...",
                    "importance": c.get("importance", "unknown")
                }
                for c in clauses[:5]
            ]
        }
        
        passed = len(clauses) > 0
        report.add_result("Clause Extractor", passed, details)
        
        logger.info(f"✓ Extracted {len(clauses)} clauses")
        logger.info(f"  Types found: {details['clause_types_found']}")
        
        return clauses
    except Exception as e:
        logger.error(f"✗ Clause Extractor failed: {e}")
        report.add_result("Clause Extractor", False, {}, str(e))
        return []


def run_risk_analyzer(report: TestReport, clauses: list) -> list:
    """Run risk analyzer."""
    logger.info("="*60)
    logger.info("TEST 2: Risk Analyzer")
    logger.info("="*60)
    
    try:
        analyzer = RiskAnalyzer()
        
        # Test with sample clauses
        test_clauses = clauses[:3] if clauses else [
            {"clause_text": "Termination with 30 days notice", "clause_type": "termination"},
            {"clause_text": "18% interest on overdue payments", "clause_type": "payment"},
            {"clause_text": "Limited liability to total fees", "clause_type": "liability"},
        ]
        
        analyzed = analyzer.analyze_batch(test_clauses)
        
        risk_distribution = {}
        for item in analyzed:
            risk_level = item.get("risk_analysis", {}).get("risk_level", "unknown")
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        details = {
            "clauses_analyzed": len(analyzed),
            "risk_distribution": risk_distribution,
            "sample_analyses": [
                {
                    "clause_type": item.get("clause_type"),
                    "risk_level": item.get("risk_analysis", {}).get("risk_level"),
                    "explanation": item.get("risk_analysis", {}).get("explanation", "")[:100]
                }
                for item in analyzed[:3]
            ]
        }
        
        passed = len(analyzed) > 0 and all("risk_analysis" in item for item in analyzed)
        report.add_result("Risk Analyzer", passed, details)
        
        logger.info(f"✓ Analyzed {len(analyzed)} clauses")
        logger.info(f"  Risk distribution: {risk_distribution}")
        
        return analyzed
    except Exception as e:
        logger.error(f"✗ Risk Analyzer failed: {e}")
        report.add_result("Risk Analyzer", False, {}, str(e))
        return []


def run_compliance_checker(report: TestReport, clauses: list) -> list:
    """Run compliance checker."""
    logger.info("="*60)
    logger.info("TEST 3: Compliance Checker")
    logger.info("="*60)
    
    try:
        checker = ComplianceChecker()
        
        # Test with key clauses
        test_clauses = [
            c for c in clauses 
            if c.get("clause_type") in ["arbitration", "termination", "liability"]
        ][:3]
        
        if not test_clauses:
            test_clauses = clauses[:2] if clauses else []
        
        checked = checker.check_batch(test_clauses) if test_clauses else []
        
        compliance_statuses = {}
        citations = []
        for item in checked:
            status = item.get("compliance_check", {}).get("compliance_status", "unknown")
            compliance_statuses[status] = compliance_statuses.get(status, 0) + 1
            
            check_data = item.get("compliance_check", {})
            if check_data.get("citations"):
                citations.extend(check_data.get("citations", []))
        
        details = {
            "clauses_checked": len(checked),
            "compliance_distribution": compliance_statuses,
            "citations_found": len(citations),
            "sample_citations": citations[:3] if citations else []
        }
        
        passed = len(checked) > 0
        report.add_result("Compliance Checker", passed, details)
        
        logger.info(f"✓ Checked {len(checked)} clauses")
        logger.info(f"  Compliance distribution: {compliance_statuses}")
        logger.info(f"  Citations found: {len(citations)}")
        
        return checked
    except Exception as e:
        logger.error(f"✗ Compliance Checker failed: {e}")
        report.add_result("Compliance Checker", False, {}, str(e))
        return []


def run_summarizer(report: TestReport) -> dict:
    """Run summarizer."""
    logger.info("="*60)
    logger.info("TEST 4: Summarizer")
    logger.info("="*60)
    
    try:
        summarizer = Summarizer()
        summary = summarizer.summarize(REAL_CONTRACT)
        
        details = {
            "summary_length": len(summary.get("summary", "")),
            "key_parties_count": len(summary.get("key_parties", [])),
            "main_obligations_count": len(summary.get("main_obligations", [])),
            "key_terms_count": len(summary.get("key_terms", [])),
            "risk_factors_count": len(summary.get("risk_factors", [])),
            "summary_preview": summary.get("summary", "")[:300] + "...",
            "key_parties": summary.get("key_parties", [])[:5]
        }
        
        passed = summary.get("summary") and len(summary.get("summary", "")) > 50
        report.add_result("Summarizer", passed, details)
        
        logger.info(f"✓ Summary generated ({len(summary.get('summary', ''))} chars)")
        logger.info(f"  Key parties: {details['key_parties_count']}")
        
        return summary
    except Exception as e:
        logger.error(f"✗ Summarizer failed: {e}")
        report.add_result("Summarizer", False, {}, str(e))
        return {}


def run_qa_agent(report: TestReport) -> list:
    """Run Q&A agent."""
    logger.info("="*60)
    logger.info("TEST 5: Q&A Agent")
    logger.info("="*60)
    
    try:
        qa = QAAgent()
        
        questions = [
            "What is the Indian Contract Act 1872?",
            "What are the provisions for arbitration in India?",
            "What is the Companies Act 2013?"
        ]
        
        answers = []
        for question in questions:
            result = qa.answer(question)
            answers.append({
                "question": question,
                "answer_length": len(result.get("answer", "")),
                "confidence": result.get("confidence"),
                "sources_count": len(result.get("sources", [])),
                "answer_preview": result.get("answer", "")[:200] + "..."
            })
            time.sleep(1)  # Delay between questions
        
        details = {
            "questions_answered": len(answers),
            "average_answer_length": sum(a["answer_length"] for a in answers) / len(answers) if answers else 0,
            "answers": answers
        }
        
        passed = len(answers) > 0 and all(a["answer_length"] > 0 for a in answers)
        report.add_result("Q&A Agent", passed, details)
        
        logger.info(f"✓ Answered {len(answers)} questions")
        
        return answers
    except Exception as e:
        logger.error(f"✗ Q&A Agent failed: {e}")
        report.add_result("Q&A Agent", False, {}, str(e))
        return []


def run_full_pipeline(report: TestReport) -> dict:
    """Run full orchestrator pipeline."""
    logger.info("="*60)
    logger.info("TEST 6: Full Document Analysis Pipeline")
    logger.info("="*60)
    
    try:
        orchestrator = get_orchestrator()
        
        result = orchestrator.analyze_document(
            contract_text=REAL_CONTRACT,
            extract_clauses=True,
            analyze_risks=True,
            check_compliance=True,
            generate_summary=True,
        )
        
        # Calculate statistics
        clauses = result.get("clauses", [])
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        compliance_counts = {"compliant": 0, "non-compliant": 0, "requires_review": 0}
        
        for clause in clauses:
            risk_level = clause.get("risk_analysis", {}).get("risk_level", "medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
            
            compliance_status = clause.get("compliance_check", {}).get("compliance_status", "requires_review")
            if compliance_status in compliance_counts:
                compliance_counts[compliance_status] += 1
        
        details = {
            "total_clauses": len(clauses),
            "risk_distribution": risk_counts,
            "compliance_distribution": compliance_counts,
            "summary_generated": result.get("summary") is not None,
            "statistics": result.get("statistics", {})
        }
        
        passed = (
            len(clauses) > 0 and
            result.get("summary") is not None and
            details["statistics"].get("total_clauses", 0) > 0
        )
        
        report.add_result("Full Pipeline", passed, details)
        
        logger.info(f"✓ Full pipeline complete")
        logger.info(f"  Total clauses: {len(clauses)}")
        logger.info(f"  Risk distribution: {risk_counts}")
        logger.info(f"  Compliance distribution: {compliance_counts}")
        
        return result
    except Exception as e:
        logger.error(f"✗ Full Pipeline failed: {e}")
        report.add_result("Full Pipeline", False, {}, str(e))
        return {}


@pytest.fixture(scope="module")
def test_report():
    return TestReport()


@pytest.fixture(scope="module")
def clauses(test_report):
    return run_clause_extractor(test_report)


@pytest.fixture(scope="module")
def risk_results(test_report, clauses):
    return run_risk_analyzer(test_report, clauses)


@pytest.fixture(scope="module")
def compliance_results(test_report, clauses):
    return run_compliance_checker(test_report, clauses)


@pytest.fixture(scope="module")
def summary_result(test_report):
    return run_summarizer(test_report)


@pytest.fixture(scope="module")
def qa_answers(test_report):
    return run_qa_agent(test_report)


@pytest.fixture(scope="module")
def full_pipeline_result(test_report):
    return run_full_pipeline(test_report)


def test_clause_extractor(clauses):
    assert len(clauses) > 0


def test_risk_analyzer(risk_results):
    assert len(risk_results) > 0


def test_compliance_checker(compliance_results):
    assert len(compliance_results) > 0


def test_summarizer(summary_result):
    assert summary_result.get("summary")


def test_qa_agent(qa_answers):
    assert len(qa_answers) >= 3


def test_full_pipeline(full_pipeline_result):
    assert len(full_pipeline_result.get("clauses", [])) > 0
    assert full_pipeline_result.get("summary") is not None


def main():
    """Run comprehensive tests."""
    report = TestReport()
    
    logger.info("Starting comprehensive Phase 2 tests...")
    logger.info(f"Testing with real contract ({len(REAL_CONTRACT)} characters)")
    
    # Run tests sequentially with delays
    clauses = run_clause_extractor(report)
    time.sleep(2)  # Delay between tests
    
    analyzed_clauses = run_risk_analyzer(report, clauses)
    time.sleep(2)
    
    checked_clauses = run_compliance_checker(report, clauses)
    time.sleep(2)
    
    summary = run_summarizer(report)
    time.sleep(2)
    
    qa_results = run_qa_agent(report)
    time.sleep(3)  # Longer delay before full pipeline
    
    full_result = run_full_pipeline(report)
    
    # Generate and print report
    final_report = report.print_report()
    
    # Save report to file
    report_file = Path(__file__).parent.parent / "results" / f"phase2_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(final_report, f, indent=2, default=str)
    
    logger.info(f"\nFull test report saved to: {report_file}")
    
    return final_report["summary"]["status"] == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

