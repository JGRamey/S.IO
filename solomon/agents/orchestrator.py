"""Enhanced agent orchestrator for coordinating multiple Solomon agents with RAG integration."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from solomon.config import settings
from .base import BaseAgent, AgentResult
from .text_sourcing import TextSourcingAgent
from .translation_tracking import TranslationTrackingAgent
from .doctrine_analysis import DoctrineAnalysisAgent
from .theme_recognition import ThemeRecognitionAgent
from .fallacy_detection import FallacyDetectionAgent


class AnalysisType(str, Enum):
    """Types of analysis that can be performed."""
    FULL_ANALYSIS = "full_analysis"
    THEME_ANALYSIS = "theme_analysis"
    DOCTRINE_ANALYSIS = "doctrine_analysis"
    FALLACY_DETECTION = "fallacy_detection"
    TRANSLATION_ANALYSIS = "translation_analysis"
    TEXT_SOURCING = "text_sourcing"
    CROSS_REFERENCE = "cross_reference"
    RAG_QUERY = "rag_query"  # New RAG-powered query type
    SEMANTIC_SEARCH = "semantic_search"  # New semantic search type


class OrchestrationRequest(BaseModel):
    """Request structure for orchestrated analysis."""
    analysis_type: AnalysisType
    text: Optional[str] = None
    text_id: Optional[str] = None
    tradition: Optional[str] = None
    denomination: Optional[str] = None
    language: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    translation_chain: Optional[List[str]] = None
    query: Optional[str] = None
    sources: Optional[List[str]] = None
    text_types: Optional[List[str]] = None  # New field for filtering text types
    enable_rag: bool = True  # New field to enable/disable RAG
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OrchestrationResult(BaseModel):
    """Enhanced result structure for orchestrated analysis."""
    success: bool
    analysis_type: AnalysisType
    data: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[Dict[str, Any]] = Field(default_factory=list)  # RAG citations
    insights: Optional[Dict[str, Any]] = None
    performance_stats: Dict[str, Any] = Field(default_factory=dict)


class AgentOrchestrator(BaseAgent):
    """Enhanced orchestrator that coordinates multiple Solomon agents with RAG integration."""
    
    def __init__(self):
        super().__init__(
            name="AgentOrchestrator",
            description="Orchestrates multiple Solomon agents for comprehensive spiritual text analysis with RAG capabilities",
            enable_rag=True
        )
        
        # Initialize agents
        self.agents = {}
        self.logger = logging.getLogger("solomon.orchestrator")
        
    async def initialize(self):
        """Initialize the orchestrator and all its agents."""
        await super().initialize()
        
        # Initialize all agents
        self.agents = {
            "text_sourcing": TextSourcingAgent(),
            "translation_tracking": TranslationTrackingAgent(),
            "doctrine_analysis": DoctrineAnalysisAgent(),
            "theme_recognition": ThemeRecognitionAgent(),
            "fallacy_detection": FallacyDetectionAgent(),
        }
        
        # Initialize each agent
        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                self.logger.info(f"Initialized {agent_name} agent")
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_name} agent: {e}")
        
        self.logger.info(f"Initialized orchestrator with {len(self.agents)} agents")
    
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Process a query using orchestration logic."""
        try:
            # Parse query to determine analysis type
            analysis_type = self._determine_analysis_type(query, context)
            
            request = OrchestrationRequest(
                analysis_type=analysis_type,
                query=query,
                text=context.get('text') if context else None,
                text_types=context.get('text_types') if context else None,
                enable_rag=context.get('enable_rag', True) if context else True,
                parameters=context or {}
            )
            
            result = await self.execute_analysis(request)
            
            return AgentResult(
                success=result.success,
                data=result.data,
                error=result.error,
                metadata=result.metadata,
                sources=result.sources
            )
            
        except Exception as e:
            self.logger.error(f"Error in orchestrator process: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={}
            )
    
    def _determine_analysis_type(self, query: str, context: Optional[Dict[str, Any]] = None) -> AnalysisType:
        """Determine the appropriate analysis type based on query and context."""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['fallacy', 'logical error', 'contradiction']):
            return AnalysisType.FALLACY_DETECTION
        elif any(keyword in query_lower for keyword in ['theme', 'topic', 'subject']):
            return AnalysisType.THEME_ANALYSIS
        elif any(keyword in query_lower for keyword in ['doctrine', 'teaching', 'belief']):
            return AnalysisType.DOCTRINE_ANALYSIS
        elif any(keyword in query_lower for keyword in ['translation', 'translate', 'language']):
            return AnalysisType.TRANSLATION_ANALYSIS
        elif any(keyword in query_lower for keyword in ['source', 'reference', 'citation']):
            return AnalysisType.TEXT_SOURCING
        elif any(keyword in query_lower for keyword in ['search', 'find', 'similar']):
            return AnalysisType.SEMANTIC_SEARCH
        elif context and context.get('enable_rag', True):
            return AnalysisType.RAG_QUERY
        else:
            return AnalysisType.FULL_ANALYSIS
    
    async def execute_analysis(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Execute orchestrated analysis based on request type."""
        start_time = datetime.now()
        
        try:
            if request.analysis_type == AnalysisType.FULL_ANALYSIS:
                result = await self._execute_full_analysis(request)
            elif request.analysis_type == AnalysisType.THEME_ANALYSIS:
                result = await self._execute_theme_analysis(request)
            elif request.analysis_type == AnalysisType.DOCTRINE_ANALYSIS:
                result = await self._execute_doctrine_analysis(request)
            elif request.analysis_type == AnalysisType.FALLACY_DETECTION:
                result = await self._execute_fallacy_detection(request)
            elif request.analysis_type == AnalysisType.TRANSLATION_ANALYSIS:
                result = await self._execute_translation_analysis(request)
            elif request.analysis_type == AnalysisType.TEXT_SOURCING:
                result = await self._execute_text_sourcing(request)
            elif request.analysis_type == AnalysisType.CROSS_REFERENCE:
                result = await self._execute_cross_reference(request)
            elif request.analysis_type == AnalysisType.RAG_QUERY:
                result = await self._execute_rag_query(request)
            elif request.analysis_type == AnalysisType.SEMANTIC_SEARCH:
                result = await self._execute_semantic_search(request)
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")
            
            # Add performance statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            result.performance_stats = {
                'execution_time': execution_time,
                'agents_used': len([k for k, v in result.data.items() if isinstance(v, dict) and 'agent_result' in str(v)]),
                'total_sources': len(result.sources)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis execution failed: {e}")
            return OrchestrationResult(
                success=False,
                analysis_type=request.analysis_type,
                data={},
                error=str(e),
                performance_stats={'execution_time': (datetime.now() - start_time).total_seconds()}
            )
    
    async def _execute_rag_query(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Execute RAG-powered query using hybrid search."""
        try:
            # Get relevant context from hybrid database
            context_texts = await self.get_context_texts(
                query=request.query,
                text_types=request.text_types,
                limit=5
            )
            
            # Generate RAG response
            response, citations = await self.generate_rag_response(
                query=request.query,
                context_texts=context_texts,
                system_prompt="You are a knowledgeable assistant specializing in spiritual and religious texts. Provide accurate, thoughtful responses based on the provided context."
            )
            
            return OrchestrationResult(
                success=True,
                analysis_type=request.analysis_type,
                data={
                    'query': request.query,
                    'response': response,
                    'context_used': len(context_texts),
                    'context_texts': context_texts[:3]  # Include top 3 for reference
                },
                sources=citations
            )
            
        except Exception as e:
            self.logger.error(f"RAG query execution failed: {e}")
            raise
    
    async def _execute_semantic_search(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Execute semantic search using vector similarity."""
        try:
            results = await self.hybrid_search(
                query=request.query,
                filters={'text_type': request.text_types} if request.text_types else None,
                limit=request.parameters.get('limit', 10),
                score_threshold=request.parameters.get('score_threshold', 0.7)
            )
            
            return OrchestrationResult(
                success=True,
                analysis_type=request.analysis_type,
                data={
                    'query': request.query,
                    'results': results,
                    'total_results': len(results)
                },
                sources=[
                    {
                        'title': result['title'],
                        'source': result.get('source_url', ''),
                        'text_type': result['text_type'],
                        'similarity_score': result.get('similarity_score', 0.0)
                    }
                    for result in results
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Semantic search execution failed: {e}")
            raise
