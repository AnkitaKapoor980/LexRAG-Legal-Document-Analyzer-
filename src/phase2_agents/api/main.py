"""
FastAPI application for Phase 2 agents.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    ExtractClausesRequest,
    ClauseResponse,
    AnalyzeRiskRequest,
    AnalyzeRiskBatchRequest,
    RiskAnalysisResponse,
    RiskAnalysisBatchResponse,
    CheckComplianceRequest,
    CheckComplianceBatchRequest,
    ComplianceCheckResponse,
    ComplianceCheckBatchResponse,
    SummarizeRequest,
    SummaryResponse,
    QARequest,
    QAResponse,
    AnalyzeDocumentRequest,
    AnalyzeDocumentResponse,
    HealthResponse,
)
from ..orchestration import get_orchestrator
from ..agents import ClauseExtractor, RiskAnalyzer, ComplianceChecker, Summarizer, QAAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LexRAG Phase 2 API",
    description="RAG & Agent API for Legal Document Analysis",
    version="0.1.0",
)

# CORS middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize orchestrator (lazy)
orchestrator = None


def get_orchestrator_instance():
    """Get orchestrator instance (lazy initialization)."""
    global orchestrator
    if orchestrator is None:
        orchestrator = get_orchestrator()
    return orchestrator


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


# Individual agent endpoints
@app.post("/api/extract-clauses", response_model=ClauseResponse)
async def extract_clauses(request: ExtractClausesRequest):
    """Extract clauses from contract text."""
    try:
        extractor = ClauseExtractor()
        clauses = extractor.extract(request.contract_text, use_llm=request.use_llm)
        return ClauseResponse(clauses=clauses)
    except Exception as e:
        logger.error(f"Clause extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-risk", response_model=RiskAnalysisResponse)
async def analyze_risk(request: AnalyzeRiskRequest):
    """Analyze risk level of a clause."""
    try:
        analyzer = RiskAnalyzer()
        risk_analysis = analyzer.analyze(request.clause_text, request.clause_type)
        return RiskAnalysisResponse(risk_analysis=risk_analysis)
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-risk-batch", response_model=RiskAnalysisBatchResponse)
async def analyze_risk_batch(request: AnalyzeRiskBatchRequest):
    """Analyze risk levels for multiple clauses."""
    try:
        analyzer = RiskAnalyzer()
        clauses_with_risks = analyzer.analyze_batch(request.clauses)
        return RiskAnalysisBatchResponse(clauses=clauses_with_risks)
    except Exception as e:
        logger.error(f"Batch risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-compliance", response_model=ComplianceCheckResponse)
async def check_compliance(request: CheckComplianceRequest):
    """Check compliance of a clause."""
    try:
        checker = ComplianceChecker()
        compliance_check = checker.check(request.clause_text, request.clause_type)
        return ComplianceCheckResponse(compliance_check=compliance_check)
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-compliance-batch", response_model=ComplianceCheckBatchResponse)
async def check_compliance_batch(request: CheckComplianceBatchRequest):
    """Check compliance for multiple clauses."""
    try:
        checker = ComplianceChecker()
        clauses_with_compliance = checker.check_batch(request.clauses)
        return ComplianceCheckBatchResponse(clauses=clauses_with_compliance)
    except Exception as e:
        logger.error(f"Batch compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize(request: SummarizeRequest):
    """Generate summary of a contract."""
    try:
        summarizer = Summarizer()
        summary = summarizer.summarize(request.contract_text, query=request.query or "contract summary")
        return SummaryResponse(summary=summary)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa", response_model=QAResponse)
async def qa(request: QARequest):
    """Answer a legal question."""
    try:
        qa_agent = QAAgent()
        result = qa_agent.answer(request.question, clear_history=request.clear_history)
        return QAResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", "medium"),
            notes=result.get("notes"),
        )
    except Exception as e:
        logger.error(f"Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Unified endpoint
@app.post("/api/analyze-document", response_model=AnalyzeDocumentResponse)
async def analyze_document(request: AnalyzeDocumentRequest):
    """Full document analysis pipeline."""
    try:
        orch = get_orchestrator_instance()
        result = orch.analyze_document(
            contract_text=request.contract_text,
            extract_clauses=request.extract_clauses,
            analyze_risks=request.analyze_risks,
            check_compliance=request.check_compliance,
            generate_summary=request.generate_summary,
        )
        return AnalyzeDocumentResponse(**result)
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

