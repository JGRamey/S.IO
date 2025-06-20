"""Agent orchestrator for coordinating multiple Solomon agents."""

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
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OrchestrationResult(BaseModel):
    """Result structure for orchestrated analysis."""
    request_id: str
    analysis_type: AnalysisType
    success: bool
    results: Dict[str, Any] = Field(default_factory=dict)
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None


class AgentOrchestrator:
    """Orchestrates multiple Solomon agents for comprehensive analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger("solomon.orchestrator")
        
        # Initialize agents
        self.agents = {
            "text_sourcing": TextSourcingAgent(),
            "translation_tracking": TranslationTrackingAgent(),
            "doctrine_analysis": DoctrineAnalysisAgent(),
            "theme_recognition": ThemeRecognitionAgent(),
            "fallacy_detection": FallacyDetectionAgent(),
        }
        
        self.logger.info(f"Initialized orchestrator with {len(self.agents)} agents")
    
    async def execute_analysis(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Execute orchestrated analysis based on request type."""
        start_time = datetime.now()
        request_id = f"req_{int(start_time.timestamp())}"
        
        try:
            self.logger.info(f"Starting {request.analysis_type} analysis (ID: {request_id})")
            
            if request.analysis_type == AnalysisType.FULL_ANALYSIS:
                results = await self._execute_full_analysis(request)
            elif request.analysis_type == AnalysisType.THEME_ANALYSIS:
                results = await self._execute_theme_analysis(request)
            elif request.analysis_type == AnalysisType.DOCTRINE_ANALYSIS:
                results = await self._execute_doctrine_analysis(request)
            elif request.analysis_type == AnalysisType.FALLACY_DETECTION:
                results = await self._execute_fallacy_detection(request)
            elif request.analysis_type == AnalysisType.TRANSLATION_ANALYSIS:
                results = await self._execute_translation_analysis(request)
            elif request.analysis_type == AnalysisType.TEXT_SOURCING:
                results = await self._execute_text_sourcing(request)
            elif request.analysis_type == AnalysisType.CROSS_REFERENCE:
                results = await self._execute_cross_reference(request)
            else:
                raise ValueError(f"Unknown analysis type: {request.analysis_type}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return OrchestrationResult(
                request_id=request_id,
                analysis_type=request.analysis_type,
                success=True,
                results=results["combined_results"],
                agent_results=results["agent_results"],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Analysis failed (ID: {request_id}): {e}")
            
            return OrchestrationResult(
                request_id=request_id,
                analysis_type=request.analysis_type,
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _execute_full_analysis(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute comprehensive analysis using all relevant agents."""
        if not request.text:
            raise ValueError("Text is required for full analysis")
        
        # Prepare input data
        base_input = {
            "text": request.text,
            "text_id": request.text_id,
            "tradition": request.tradition,
            "denomination": request.denomination,
            "language": request.language,
        }
        
        # Execute agents in parallel
        tasks = {
            "theme_recognition": self.agents["theme_recognition"].execute(base_input),
            "doctrine_analysis": self.agents["doctrine_analysis"].execute(base_input),
            "fallacy_detection": self.agents["fallacy_detection"].execute(base_input),
        }
        
        # Wait for all agents to complete
        agent_results = {}
        for agent_name, task in tasks.items():
            try:
                result = await task
                agent_results[agent_name] = result
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                agent_results[agent_name] = AgentResult(
                    success=False,
                    error=str(e)
                )
        
        # Combine results
        combined_results = self._combine_analysis_results(agent_results, request)
        
        return {
            "agent_results": agent_results,
            "combined_results": combined_results
        }
    
    async def _execute_theme_analysis(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute theme recognition analysis."""
        if not request.text:
            raise ValueError("Text is required for theme analysis")
        
        input_data = {
            "text": request.text,
            "text_id": request.text_id,
            "tradition": request.tradition,
            "language": request.language,
        }
        
        result = await self.agents["theme_recognition"].execute(input_data)
        
        return {
            "agent_results": {"theme_recognition": result},
            "combined_results": result.data if result.success else {}
        }
    
    async def _execute_doctrine_analysis(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute doctrine analysis."""
        if not request.text:
            raise ValueError("Text is required for doctrine analysis")
        
        input_data = {
            "text": request.text,
            "text_id": request.text_id,
            "tradition": request.tradition,
            "denomination": request.denomination,
        }
        
        result = await self.agents["doctrine_analysis"].execute(input_data)
        
        return {
            "agent_results": {"doctrine_analysis": result},
            "combined_results": result.data if result.success else {}
        }
    
    async def _execute_fallacy_detection(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute fallacy detection analysis."""
        if not request.text:
            raise ValueError("Text is required for fallacy detection")
        
        input_data = {
            "text": request.text,
            "text_id": request.text_id,
            "context": request.parameters.get("context", ""),
        }
        
        result = await self.agents["fallacy_detection"].execute(input_data)
        
        return {
            "agent_results": {"fallacy_detection": result},
            "combined_results": result.data if result.success else {}
        }
    
    async def _execute_translation_analysis(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute translation analysis."""
        if not request.original_text or not request.translated_text:
            raise ValueError("Both original_text and translated_text are required for translation analysis")
        
        input_data = {
            "original_text": request.original_text,
            "translated_text": request.translated_text,
            "source_language": request.source_language,
            "target_language": request.target_language,
            "translation_chain": request.translation_chain,
            "text_id": request.text_id,
        }
        
        result = await self.agents["translation_tracking"].execute(input_data)
        
        return {
            "agent_results": {"translation_tracking": result},
            "combined_results": result.data if result.success else {}
        }
    
    async def _execute_text_sourcing(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute text sourcing."""
        if not request.query:
            raise ValueError("Query is required for text sourcing")
        
        input_data = {
            "query": request.query,
            "text_type": request.parameters.get("text_type"),
            "language": request.language,
            "sources": request.sources,
        }
        
        result = await self.agents["text_sourcing"].execute(input_data)
        
        return {
            "agent_results": {"text_sourcing": result},
            "combined_results": result.data if result.success else {}
        }
    
    async def _execute_cross_reference(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute cross-reference analysis across multiple texts."""
        if not request.text:
            raise ValueError("Text is required for cross-reference analysis")
        
        # First, perform theme and doctrine analysis
        base_input = {
            "text": request.text,
            "text_id": request.text_id,
            "tradition": request.tradition,
            "denomination": request.denomination,
            "language": request.language,
        }
        
        # Execute theme and doctrine analysis
        theme_result = await self.agents["theme_recognition"].execute(base_input)
        doctrine_result = await self.agents["doctrine_analysis"].execute(base_input)
        
        # Find cross-references based on themes and doctrines
        cross_references = await self._find_cross_references(theme_result, doctrine_result, request)
        
        agent_results = {
            "theme_recognition": theme_result,
            "doctrine_analysis": doctrine_result,
        }
        
        combined_results = {
            "themes": theme_result.data if theme_result.success else {},
            "doctrines": doctrine_result.data if doctrine_result.success else {},
            "cross_references": cross_references,
        }
        
        return {
            "agent_results": agent_results,
            "combined_results": combined_results
        }
    
    def _combine_analysis_results(
        self, 
        agent_results: Dict[str, AgentResult], 
        request: OrchestrationRequest
    ) -> Dict[str, Any]:
        """Combine results from multiple agents into a unified analysis."""
        combined = {
            "text_id": request.text_id,
            "tradition": request.tradition,
            "denomination": request.denomination,
            "language": request.language,
            "analysis_summary": {},
            "themes": {},
            "doctrines": {},
            "fallacies": {},
            "insights": [],
            "cross_tradition_connections": [],
        }
        
        # Extract theme analysis
        if "theme_recognition" in agent_results and agent_results["theme_recognition"].success:
            theme_data = agent_results["theme_recognition"].data
            combined["themes"] = theme_data
            combined["analysis_summary"]["themes_detected"] = theme_data.get("themes_detected", 0)
        
        # Extract doctrine analysis
        if "doctrine_analysis" in agent_results and agent_results["doctrine_analysis"].success:
            doctrine_data = agent_results["doctrine_analysis"].data
            combined["doctrines"] = doctrine_data
            combined["analysis_summary"]["doctrines_detected"] = doctrine_data.get("doctrines_detected", 0)
        
        # Extract fallacy analysis
        if "fallacy_detection" in agent_results and agent_results["fallacy_detection"].success:
            fallacy_data = agent_results["fallacy_detection"].data
            combined["fallacies"] = fallacy_data
            combined["analysis_summary"]["fallacies_detected"] = fallacy_data.get("fallacies_detected", 0)
        
        # Generate insights
        combined["insights"] = self._generate_insights(agent_results, request)
        
        # Find cross-tradition connections
        combined["cross_tradition_connections"] = self._find_tradition_connections(agent_results)
        
        # Overall analysis score
        combined["analysis_summary"]["overall_score"] = self._calculate_overall_score(agent_results)
        
        return combined
    
    def _generate_insights(
        self, 
        agent_results: Dict[str, AgentResult], 
        request: OrchestrationRequest
    ) -> List[str]:
        """Generate insights based on combined agent results."""
        insights = []
        
        # Theme-based insights
        if "theme_recognition" in agent_results and agent_results["theme_recognition"].success:
            theme_data = agent_results["theme_recognition"].data
            themes_count = theme_data.get("themes_detected", 0)
            
            if themes_count > 5:
                insights.append("This text contains multiple universal spiritual themes, suggesting rich theological content")
            elif themes_count > 0:
                most_confident = theme_data.get("analysis_summary", {}).get("most_confident_theme")
                if most_confident:
                    insights.append(f"The dominant spiritual theme appears to be '{most_confident}'")
        
        # Doctrine-based insights
        if "doctrine_analysis" in agent_results and agent_results["doctrine_analysis"].success:
            doctrine_data = agent_results["doctrine_analysis"].data
            doctrines_count = doctrine_data.get("doctrines_detected", 0)
            
            if doctrines_count > 3:
                insights.append("This text contains multiple specific religious doctrines, indicating doctrinal focus")
            
            traditions = doctrine_data.get("analysis_summary", {}).get("traditions", {})
            if len(traditions) > 1:
                insights.append("This text references doctrines from multiple religious traditions")
        
        # Fallacy-based insights
        if "fallacy_detection" in agent_results and agent_results["fallacy_detection"].success:
            fallacy_data = agent_results["fallacy_detection"].data
            fallacies_count = fallacy_data.get("fallacies_detected", 0)
            
            if fallacies_count > 3:
                insights.append("This text contains multiple logical fallacies, suggesting argumentative or polemical content")
            elif fallacies_count == 0:
                insights.append("No significant logical fallacies detected, indicating sound reasoning")
        
        # Cross-agent insights
        theme_success = "theme_recognition" in agent_results and agent_results["theme_recognition"].success
        doctrine_success = "doctrine_analysis" in agent_results and agent_results["doctrine_analysis"].success
        
        if theme_success and doctrine_success:
            theme_count = agent_results["theme_recognition"].data.get("themes_detected", 0)
            doctrine_count = agent_results["doctrine_analysis"].data.get("doctrines_detected", 0)
            
            if theme_count > doctrine_count:
                insights.append("This text emphasizes universal spiritual themes over specific doctrines")
            elif doctrine_count > theme_count:
                insights.append("This text focuses more on specific religious doctrines than universal themes")
        
        return insights
    
    def _find_tradition_connections(self, agent_results: Dict[str, AgentResult]) -> List[Dict[str, Any]]:
        """Find connections between different religious traditions."""
        connections = []
        
        # Extract themes with cross-references
        if "theme_recognition" in agent_results and agent_results["theme_recognition"].success:
            theme_data = agent_results["theme_recognition"].data
            cross_refs = theme_data.get("cross_references", {})
            
            for theme, traditions in cross_refs.items():
                if traditions:
                    connections.append({
                        "type": "theme",
                        "element": theme,
                        "connected_traditions": traditions,
                        "description": f"The theme '{theme}' appears across {len(traditions)} traditions"
                    })
        
        # Extract doctrine connections
        if "doctrine_analysis" in agent_results and agent_results["doctrine_analysis"].success:
            doctrine_data = agent_results["doctrine_analysis"].data
            traditions = doctrine_data.get("analysis_summary", {}).get("traditions", {})
            
            if len(traditions) > 1:
                tradition_list = list(traditions.keys())
                connections.append({
                    "type": "doctrinal",
                    "element": "multiple_traditions",
                    "connected_traditions": tradition_list,
                    "description": f"This text contains doctrines from {len(tradition_list)} different traditions"
                })
        
        return connections
    
    def _calculate_overall_score(self, agent_results: Dict[str, AgentResult]) -> float:
        """Calculate an overall analysis quality score."""
        total_score = 0.0
        agent_count = 0
        
        for agent_name, result in agent_results.items():
            if result.success and result.data:
                agent_count += 1
                
                # Get confidence scores from different agents
                if agent_name == "theme_recognition":
                    avg_confidence = result.data.get("analysis_summary", {}).get("average_confidence", 0.5)
                    total_score += avg_confidence
                elif agent_name == "doctrine_analysis":
                    avg_confidence = result.data.get("analysis_summary", {}).get("average_confidence", 0.5)
                    total_score += avg_confidence
                elif agent_name == "fallacy_detection":
                    avg_confidence = result.data.get("analysis_summary", {}).get("average_confidence", 0.5)
                    total_score += avg_confidence
                else:
                    total_score += 0.7  # Default score for successful execution
        
        return total_score / agent_count if agent_count > 0 else 0.0
    
    async def _find_cross_references(
        self,
        theme_result: AgentResult,
        doctrine_result: AgentResult,
        request: OrchestrationRequest
    ) -> Dict[str, Any]:
        """Find cross-references based on theme and doctrine analysis."""
        cross_refs = {
            "similar_themes": [],
            "related_doctrines": [],
            "tradition_overlaps": [],
        }
        
        # Extract themes for cross-referencing
        if theme_result.success and theme_result.data:
            themes = theme_result.data.get("themes", [])
            for theme in themes:
                if isinstance(theme, dict):
                    theme_name = theme.get("theme_name", "")
                    if theme_name:
                        cross_refs["similar_themes"].append({
                            "theme": theme_name,
                            "confidence": theme.get("confidence_score", 0.0),
                            "traditions": theme.get("cross_references", [])
                        })
        
        # Extract doctrines for cross-referencing
        if doctrine_result.success and doctrine_result.data:
            doctrines = doctrine_result.data.get("doctrines", [])
            for doctrine in doctrines:
                if isinstance(doctrine, dict):
                    doctrine_name = doctrine.get("doctrine_name", "")
                    if doctrine_name:
                        cross_refs["related_doctrines"].append({
                            "doctrine": doctrine_name,
                            "tradition": doctrine.get("tradition", ""),
                            "confidence": doctrine.get("confidence_score", 0.0)
                        })
        
        return cross_refs
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all agents."""
        health_status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                health_status[agent_name] = await agent.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for {agent_name}: {e}")
                health_status[agent_name] = False
        
        return health_status
    
    async def close(self):
        """Close all agents and cleanup resources."""
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'close'):
                    await agent.close()
            except Exception as e:
                self.logger.error(f"Error closing agent {agent_name}: {e}")
        
        self.logger.info("Agent orchestrator closed")
