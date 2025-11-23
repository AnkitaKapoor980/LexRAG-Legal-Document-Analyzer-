"""
Pydantic schemas for API request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Request Schemas
class ExtractClausesRequest(BaseModel):
    """Request for clause extraction."""
    contract_text: str = Field(..., description="Contract text to analyze")
    use_llm: bool = Field(True, description="Whether to use LLM for extraction")


class AnalyzeRiskRequest(BaseModel):
    """Request for risk analysis."""
    clause_text: str = Field(..., description="Clause text to analyze")
    clause_type: str = Field("unknown", description="Type of clause")


class AnalyzeRiskBatchRequest(BaseModel):
    """Request for batch risk analysis."""
    clauses: List[Dict[str, Any]] = Field(..., description="List of clauses to analyze")


class CheckComplianceRequest(BaseModel):
    """Request for compliance check."""
    clause_text: str = Field(..., description="Clause text to check")
    clause_type: str = Field("unknown", description="Type of clause")


class CheckComplianceBatchRequest(BaseModel):
    """Request for batch compliance check."""
    clauses: List[Dict[str, Any]] = Field(..., description="List of clauses to check")


class SummarizeRequest(BaseModel):
    """Request for document summarization."""
    contract_text: str = Field(..., description="Contract text to summarize")
    query: Optional[str] = Field(None, description="Optional query to focus summary")


class QARequest(BaseModel):
    """Request for Q&A."""
    question: str = Field(..., description="Question to answer")
    clear_history: bool = Field(False, description="Whether to clear conversation history")


class AnalyzeDocumentRequest(BaseModel):
    """Request for full document analysis."""
    contract_text: str = Field(..., description="Contract text to analyze")
    extract_clauses: bool = Field(True, description="Whether to extract clauses")
    analyze_risks: bool = Field(True, description="Whether to analyze risks")
    check_compliance: bool = Field(True, description="Whether to check compliance")
    generate_summary: bool = Field(True, description="Whether to generate summary")


# Response Schemas
class ClauseResponse(BaseModel):
    """Clause extraction response."""
    clauses: List[Dict[str, Any]] = Field(..., description="Extracted clauses")


class RiskAnalysisResponse(BaseModel):
    """Risk analysis response."""
    risk_analysis: Dict[str, Any] = Field(..., description="Risk analysis result")


class RiskAnalysisBatchResponse(BaseModel):
    """Batch risk analysis response."""
    clauses: List[Dict[str, Any]] = Field(..., description="Clauses with risk analysis")


class ComplianceCheckResponse(BaseModel):
    """Compliance check response."""
    compliance_check: Dict[str, Any] = Field(..., description="Compliance check result")


class ComplianceCheckBatchResponse(BaseModel):
    """Batch compliance check response."""
    clauses: List[Dict[str, Any]] = Field(..., description="Clauses with compliance check")


class SummaryResponse(BaseModel):
    """Summary response."""
    summary: Dict[str, Any] = Field(..., description="Generated summary")


class QAResponse(BaseModel):
    """Q&A response."""
    answer: str = Field(..., description="Answer to the question")
    sources: List[Dict[str, str]] = Field(..., description="Source citations")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    notes: Optional[str] = Field(None, description="Additional notes")


class AnalyzeDocumentResponse(BaseModel):
    """Full document analysis response."""
    document_length: int = Field(..., description="Length of document")
    clauses: List[Dict[str, Any]] = Field(..., description="Extracted and analyzed clauses")
    summary: Optional[Dict[str, Any]] = Field(None, description="Generated summary")
    statistics: Dict[str, Any] = Field(..., description="Analysis statistics")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

