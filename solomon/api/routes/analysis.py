"""Analysis API routes."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from solomon.database import get_db_session
from solomon.agents.orchestrator import AgentOrchestrator, OrchestrationRequest, AnalysisType

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoints."""
    text: Optional[str] = None
    text_id: Optional[str] = None
    tradition: Optional[str] = None
    denomination: Optional[str] = None
    language: Optional[str] = "english"
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    translation_chain: Optional[List[str]] = None
    query: Optional[str] = None
    sources: Optional[List[str]] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoints."""
    request_id: str
    analysis_type: str
    success: bool
    results: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    error: Optional[str] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator dependency."""
    from solomon.api.main import orchestrator
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    return orchestrator


@router.post("/full", response_model=AnalysisResponse)
async def full_analysis(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Perform comprehensive analysis of spiritual text."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for full analysis")
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.FULL_ANALYSIS,
        text=request.text,
        text_id=request.text_id,
        tradition=request.tradition,
        denomination=request.denomination,
        language=request.language,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.post("/themes", response_model=AnalysisResponse)
async def theme_analysis(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze universal themes in spiritual text."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for theme analysis")
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.THEME_ANALYSIS,
        text=request.text,
        text_id=request.text_id,
        tradition=request.tradition,
        language=request.language,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.post("/doctrines", response_model=AnalysisResponse)
async def doctrine_analysis(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze religious doctrines in spiritual text."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for doctrine analysis")
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.DOCTRINE_ANALYSIS,
        text=request.text,
        text_id=request.text_id,
        tradition=request.tradition,
        denomination=request.denomination,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.post("/fallacies", response_model=AnalysisResponse)
async def fallacy_detection(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Detect logical fallacies in spiritual text."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for fallacy detection")
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.FALLACY_DETECTION,
        text=request.text,
        text_id=request.text_id,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.post("/translation", response_model=AnalysisResponse)
async def translation_analysis(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze translation quality and track changes."""
    if not request.original_text or not request.translated_text:
        raise HTTPException(
            status_code=400, 
            detail="Both original_text and translated_text are required for translation analysis"
        )
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.TRANSLATION_ANALYSIS,
        original_text=request.original_text,
        translated_text=request.translated_text,
        source_language=request.source_language,
        target_language=request.target_language,
        translation_chain=request.translation_chain,
        text_id=request.text_id,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.post("/cross-reference", response_model=AnalysisResponse)
async def cross_reference_analysis(
    request: AnalysisRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Find cross-references and connections across traditions."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for cross-reference analysis")
    
    orchestration_request = OrchestrationRequest(
        analysis_type=AnalysisType.CROSS_REFERENCE,
        text=request.text,
        text_id=request.text_id,
        tradition=request.tradition,
        denomination=request.denomination,
        language=request.language,
        parameters=request.parameters
    )
    
    result = await orchestrator.execute_analysis(orchestration_request)
    
    return AnalysisResponse(
        request_id=result.request_id,
        analysis_type=result.analysis_type.value,
        success=result.success,
        results=result.results,
        execution_time=result.execution_time,
        timestamp=result.timestamp,
        error=result.error
    )


@router.get("/types")
async def get_analysis_types():
    """Get available analysis types."""
    return {
        "analysis_types": [
            {
                "type": "full_analysis",
                "name": "Full Analysis",
                "description": "Comprehensive analysis including themes, doctrines, and fallacies"
            },
            {
                "type": "theme_analysis", 
                "name": "Theme Analysis",
                "description": "Identify universal spiritual themes across traditions"
            },
            {
                "type": "doctrine_analysis",
                "name": "Doctrine Analysis", 
                "description": "Analyze specific religious doctrines and beliefs"
            },
            {
                "type": "fallacy_detection",
                "name": "Fallacy Detection",
                "description": "Detect logical fallacies in arguments and reasoning"
            },
            {
                "type": "translation_analysis",
                "name": "Translation Analysis",
                "description": "Analyze translation quality and track linguistic changes"
            },
            {
                "type": "cross_reference",
                "name": "Cross-Reference Analysis",
                "description": "Find connections and parallels across different traditions"
            }
        ]
    }


@router.get("/traditions")
async def get_supported_traditions():
    """Get supported religious traditions."""
    return {
        "traditions": [
            {"name": "Christianity", "denominations": ["Catholic", "Protestant", "Orthodox", "Baptist", "Lutheran"]},
            {"name": "Islam", "denominations": ["Sunni", "Shia", "Sufi"]},
            {"name": "Judaism", "denominations": ["Orthodox", "Conservative", "Reform"]},
            {"name": "Hinduism", "denominations": ["Advaita", "Dvaita", "Vishishtadvaita"]},
            {"name": "Buddhism", "denominations": ["Theravada", "Mahayana", "Vajrayana"]},
            {"name": "Taoism", "denominations": []},
            {"name": "Sikhism", "denominations": []},
            {"name": "Gnosticism", "denominations": []},
            {"name": "Zoroastrianism", "denominations": []}
        ]
    }


@router.get("/languages")
async def get_supported_languages():
    """Get supported languages."""
    return {
        "languages": [
            {"code": "english", "name": "English"},
            {"code": "hebrew", "name": "Hebrew"},
            {"code": "aramaic", "name": "Aramaic"},
            {"code": "greek", "name": "Greek"},
            {"code": "latin", "name": "Latin"},
            {"code": "arabic", "name": "Arabic"},
            {"code": "sanskrit", "name": "Sanskrit"}
        ]
    }
