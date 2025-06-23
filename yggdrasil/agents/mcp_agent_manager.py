#!/usr/bin/env python3
"""
MCP Agent Manager - Integrates all Yggdrasil agents with MCP server
Provides unified interface for all AI agents through MCP protocol
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# MCP imports
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest, CallToolResult

# Agent imports
from .base import BaseAgent, AgentResult
from .theme_recognition import ThemeRecognitionAgent
from .doctrine_analysis import DoctrineAnalysisAgent  
from .fallacy_detection import FallacyDetectionAgent
from .translation_tracking import TranslationTrackingAgent
from .text_sourcing import TextSourcingAgent
from .smart_storage_agent import SmartStorageAgent
from .bias_detection import BiasDetectionAgent
from .orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analysis available through MCP"""
    THEME_ANALYSIS = "theme_analysis"
    DOCTRINE_ANALYSIS = "doctrine_analysis"
    FALLACY_DETECTION = "fallacy_detection"
    TRANSLATION_ANALYSIS = "translation_analysis"
    TEXT_SOURCING = "text_sourcing"
    STORAGE_OPTIMIZATION = "storage_optimization"
    BIAS_DETECTION = "bias_detection"
    CONTENT_ANALYSIS = "content_analysis"
    CROSS_REFERENCE = "cross_reference"
    COMPREHENSIVE = "comprehensive"

@dataclass
class MCPAnalysisRequest:
    """Request structure for MCP agent analysis"""
    analysis_type: AnalysisType
    text: str
    url: Optional[str] = None
    domain: Optional[str] = None
    tradition: Optional[str] = None
    language: Optional[str] = "en"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MCPAnalysisResult:
    """Result structure for MCP agent analysis"""
    success: bool
    analysis_type: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float
    timestamp: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MCPAgentManager:
    """Manager for all Yggdrasil agents integrated with MCP server"""
    
    def __init__(self, postgres_url: str, qdrant_url: str):
        self.postgres_url = postgres_url
        self.qdrant_url = qdrant_url
        
        # Initialize agents
        self.agents = {}
        self.orchestrator = None
        self.storage_agent = None
        
        # Performance tracking
        self.analysis_history = []
        self.performance_stats = {}
        
    async def initialize(self):
        """Initialize all agents"""
        try:
            logger.info("Initializing MCP Agent Manager...")
            
            # Initialize storage agent (our new intelligent storage system)
            self.storage_agent = SmartStorageAgent(self.postgres_url, self.qdrant_url)
            await self.storage_agent.initialize()
            
            # Initialize content analysis agents
            self.agents = {
                'theme_recognition': ThemeRecognitionAgent(),
                'doctrine_analysis': DoctrineAnalysisAgent(),
                'fallacy_detection': FallacyDetectionAgent(),
                'translation_tracking': TranslationTrackingAgent(),
                'text_sourcing': TextSourcingAgent(),
                'bias_detection': BiasDetectionAgent()
            }
            
            # Initialize each agent
            for name, agent in self.agents.items():
                await agent.initialize()
                logger.info(f"Initialized {name} agent")
            
            # Initialize orchestrator
            self.orchestrator = AgentOrchestrator()
            await self.orchestrator.initialize()
            
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    async def analyze_content(self, request: MCPAnalysisRequest) -> MCPAnalysisResult:
        """Perform content analysis using specified agent"""
        
        start_time = datetime.utcnow()
        
        try:
            if request.analysis_type == AnalysisType.THEME_ANALYSIS:
                result = await self._analyze_themes(request)
            
            elif request.analysis_type == AnalysisType.DOCTRINE_ANALYSIS:
                result = await self._analyze_doctrines(request)
            
            elif request.analysis_type == AnalysisType.FALLACY_DETECTION:
                result = await self._detect_fallacies(request)
            
            elif request.analysis_type == AnalysisType.TRANSLATION_ANALYSIS:
                result = await self._analyze_translation(request)
            
            elif request.analysis_type == AnalysisType.TEXT_SOURCING:
                result = await self._analyze_sources(request)
            
            elif request.analysis_type == AnalysisType.STORAGE_OPTIMIZATION:
                result = await self._optimize_storage(request)
            
            elif request.analysis_type == AnalysisType.CONTENT_ANALYSIS:
                result = await self._analyze_content_intelligence(request)
            
            elif request.analysis_type == AnalysisType.COMPREHENSIVE:
                result = await self._comprehensive_analysis(request)
            
            elif request.analysis_type == AnalysisType.BIAS_DETECTION:
                result = await self._detect_bias(request)
            
            else:
                raise ValueError(f"Unknown analysis type: {request.analysis_type}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Track performance
            self._track_performance(request.analysis_type, processing_time, True)
            
            return MCPAnalysisResult(
                success=True,
                analysis_type=request.analysis_type.value,
                results=result,
                metadata=request.metadata,
                processing_time=processing_time,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._track_performance(request.analysis_type, processing_time, False)
            
            logger.error(f"Error in content analysis: {e}")
            
            return MCPAnalysisResult(
                success=False,
                analysis_type=request.analysis_type.value,
                results={},
                metadata=request.metadata,
                processing_time=processing_time,
                timestamp=datetime.utcnow().isoformat(),
                error_message=str(e)
            )
    
    async def _analyze_themes(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Analyze themes in content"""
        agent = self.agents['theme_recognition']
        
        # Updated to work with enhanced Yggdrasil schema
        result = await agent.analyze_text(
            text=request.text,
            tradition=request.tradition,
            enable_cross_reference=True
        )
        
        return {
            "detected_themes": result.data.get("themes", []),
            "cross_references": result.data.get("cross_references", []),
            "confidence_scores": result.data.get("confidence_scores", {}),
            "universal_patterns": result.data.get("universal_patterns", [])
        }
    
    async def _analyze_doctrines(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Analyze doctrines in content"""
        agent = self.agents['doctrine_analysis']
        
        result = await agent.analyze_text(
            text=request.text,
            tradition=request.tradition,
            denomination=request.metadata.get('denomination')
        )
        
        return {
            "detected_doctrines": result.data.get("doctrines", []),
            "tradition_analysis": result.data.get("tradition_analysis", {}),
            "historical_context": result.data.get("historical_context", []),
            "doctrinal_evolution": result.data.get("evolution", [])
        }
    
    async def _detect_fallacies(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Detect logical fallacies in content"""
        agent = self.agents['fallacy_detection']
        
        result = await agent.analyze_text(
            text=request.text,
            context=request.metadata
        )
        
        return {
            "detected_fallacies": result.data.get("fallacies", []),
            "logical_structure": result.data.get("logical_structure", {}),
            "argument_quality": result.data.get("argument_quality", 0),
            "recommendations": result.data.get("recommendations", [])
        }
    
    async def _analyze_translation(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Analyze translation quality and issues"""
        agent = self.agents['translation_tracking']
        
        # Requires original and translated text
        original = request.metadata.get('original_text', request.text)
        translated = request.metadata.get('translated_text', request.text)
        
        result = await agent.analyze_translation(
            original_text=original,
            translated_text=translated,
            source_language=request.metadata.get('source_language', 'auto'),
            target_language=request.language
        )
        
        return {
            "translation_quality": result.data.get("quality_score", 0),
            "detected_issues": result.data.get("issues", []),
            "cultural_adaptations": result.data.get("cultural_notes", []),
            "improvement_suggestions": result.data.get("suggestions", [])
        }
    
    async def _analyze_sources(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Analyze text sources and citations"""
        agent = self.agents['text_sourcing']
        
        result = await agent.analyze_text(
            text=request.text,
            url=request.url,
            tradition=request.tradition
        )
        
        return {
            "identified_sources": result.data.get("sources", []),
            "citation_quality": result.data.get("citation_quality", 0),
            "authenticity_score": result.data.get("authenticity", 0),
            "source_recommendations": result.data.get("recommendations", [])
        }
    
    async def _optimize_storage(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Optimize storage for content using intelligent storage agent"""
        
        # Use our smart storage agent for optimization
        analysis = await self.storage_agent.analyze_content(
            url=request.url or "manual_input",
            content=request.text,
            metadata=request.metadata
        )
        
        return {
            "storage_strategy": analysis.storage_decision.value,
            "confidence_score": analysis.confidence_score,
            "reasoning": analysis.reasoning,
            "complexity_metrics": {
                "semantic_complexity": analysis.semantic_complexity,
                "topic_coherence": analysis.topic_coherence,
                "information_density": analysis.information_density,
                "query_potential": analysis.query_potential
            },
            "optimization_recommendations": await self.storage_agent.optimize_storage_performance()
        }
    
    async def _analyze_content_intelligence(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Perform intelligent content analysis combining multiple agents"""
        
        # Run theme and doctrine analysis in parallel
        theme_task = self._analyze_themes(request)
        doctrine_task = self._analyze_doctrines(request)
        storage_task = self._optimize_storage(request)
        
        theme_result, doctrine_result, storage_result = await asyncio.gather(
            theme_task, doctrine_task, storage_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(theme_result, Exception):
            theme_result = {"error": str(theme_result)}
        if isinstance(doctrine_result, Exception):
            doctrine_result = {"error": str(doctrine_result)}
        if isinstance(storage_result, Exception):
            storage_result = {"error": str(storage_result)}
        
        return {
            "theme_analysis": theme_result,
            "doctrine_analysis": doctrine_result,
            "storage_optimization": storage_result,
            "content_classification": {
                "domain": request.domain,
                "estimated_complexity": storage_result.get("complexity_metrics", {}).get("semantic_complexity", 0.5),
                "recommended_storage": storage_result.get("storage_strategy", "hybrid_optimal")
            }
        }
    
    async def _comprehensive_analysis(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Perform comprehensive analysis using orchestrator"""
        
        # Use the orchestrator for comprehensive analysis
        if self.orchestrator:
            from .orchestrator import OrchestrationRequest, AnalysisType as OrchestrationType
            
            orchestration_request = OrchestrationRequest(
                analysis_type=OrchestrationType.FULL_ANALYSIS,
                text=request.text,
                tradition=request.tradition,
                language=request.language,
                enable_rag=True,
                parameters=request.metadata
            )
            
            result = await self.orchestrator.execute_analysis(orchestration_request)
            
            return {
                "comprehensive_results": result.data,
                "cross_references": result.sources,
                "insights": result.insights,
                "performance_stats": result.performance_stats
            }
        else:
            # Fallback to combined analysis
            return await self._analyze_content_intelligence(request)
    
    async def _detect_bias(self, request: MCPAnalysisRequest) -> Dict[str, Any]:
        """Detect bias in content"""
        agent = self.agents['bias_detection']
        
        result = await agent.analyze_text(
            text=request.text,
            domain=request.domain,
            tradition=request.tradition,
            context=request.metadata.get('context', ''),
            sensitivity=request.metadata.get('sensitivity', 'medium')
        )
        
        return {
            "detected_biases": result.data.get("detected_biases", []),
            "bias_summary": result.data.get("bias_summary", {}),
            "recommendations": result.data.get("recommendations", []),
            "overall_bias_score": result.data.get("overall_bias_score", 0.0),
            "analysis_metadata": result.data.get("analysis_metadata", {})
        }
    
    def _track_performance(self, analysis_type: AnalysisType, processing_time: float, success: bool):
        """Track performance metrics for analyses"""
        
        type_name = analysis_type.value
        
        if type_name not in self.performance_stats:
            self.performance_stats[type_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "error_count": 0
            }
        
        stats = self.performance_stats[type_name]
        stats["total_requests"] += 1
        stats["total_time"] += processing_time
        stats["avg_time"] = stats["total_time"] / stats["total_requests"]
        
        if success:
            stats["successful_requests"] += 1
        else:
            stats["error_count"] += 1
        
        # Store in history
        self.analysis_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": type_name,
            "processing_time": processing_time,
            "success": success
        })
        
        # Keep only last 1000 entries
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-1000:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        
        return {
            "agent_performance": self.performance_stats,
            "total_analyses": len(self.analysis_history),
            "recent_analyses": self.analysis_history[-10:] if self.analysis_history else [],
            "overall_success_rate": sum(1 for h in self.analysis_history if h["success"]) / len(self.analysis_history) if self.analysis_history else 0,
            "avg_processing_time": sum(h["processing_time"] for h in self.analysis_history) / len(self.analysis_history) if self.analysis_history else 0
        }
    
    def get_available_analyses(self) -> List[Dict[str, str]]:
        """Get list of available analysis types"""
        
        return [
            {
                "type": "theme_analysis",
                "name": "Theme Recognition",
                "description": "Identify universal themes across spiritual traditions"
            },
            {
                "type": "doctrine_analysis", 
                "name": "Doctrine Analysis",
                "description": "Analyze religious doctrines and theological concepts"
            },
            {
                "type": "fallacy_detection",
                "name": "Fallacy Detection",
                "description": "Detect logical fallacies and argument weaknesses"
            },
            {
                "type": "translation_analysis",
                "name": "Translation Analysis", 
                "description": "Analyze translation quality and cultural adaptations"
            },
            {
                "type": "text_sourcing",
                "name": "Source Analysis",
                "description": "Identify and verify text sources and citations"
            },
            {
                "type": "storage_optimization",
                "name": "Storage Optimization",
                "description": "Optimize content storage strategy using AI"
            },
            {
                "type": "content_analysis",
                "name": "Intelligent Content Analysis",
                "description": "Combined analysis using multiple AI agents"
            },
            {
                "type": "bias_detection",
                "name": "Bias Detection",
                "description": "Detect bias in content"
            },
            {
                "type": "comprehensive",
                "name": "Comprehensive Analysis",
                "description": "Complete analysis using all available agents"
            }
        ]
