"""AI Agents package for Solomon project."""

from .base import BaseAgent
from .text_sourcing import TextSourcingAgent
from .translation_tracking import TranslationTrackingAgent
from .doctrine_analysis import DoctrineAnalysisAgent
from .theme_recognition import ThemeRecognitionAgent
from .fallacy_detection import FallacyDetectionAgent
from .orchestrator import AgentOrchestrator

__all__ = [
    "BaseAgent",
    "TextSourcingAgent", 
    "TranslationTrackingAgent",
    "DoctrineAnalysisAgent",
    "ThemeRecognitionAgent",
    "FallacyDetectionAgent",
    "AgentOrchestrator",
]
