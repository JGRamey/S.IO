"""AI Agents package for Solomon project."""

from .base import BaseAgent
from .text_sourcing import TextSourcingAgent
from .translation_tracking import TranslationTrackingAgent
from .doctrine_analysis import DoctrineAnalysisAgent
from .theme_recognition import ThemeRecognitionAgent
from .fallacy_detection import FallacyDetectionAgent
from .bias_detection import BiasDetectionAgent
from .smart_storage_agent import SmartStorageAgent
from .orchestrator import AgentOrchestrator
from .mcp_agent_manager import MCPAgentManager

__all__ = [
    "BaseAgent",
    "TextSourcingAgent", 
    "TranslationTrackingAgent",
    "DoctrineAnalysisAgent",
    "ThemeRecognitionAgent",
    "FallacyDetectionAgent",
    "BiasDetectionAgent",
    "SmartStorageAgent",
    "AgentOrchestrator",
    "MCPAgentManager",
]
