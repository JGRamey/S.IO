"""Database package for Solomon project."""

from .models import (
    Base,
    SpiritualText,
    Translation,
    Doctrine,
    DoctrineReference,
    Theme,
    ThemeReference,
    LogicalFallacy,
    Contradiction,
    AnalysisSession,
    TextType,
    Language,
)
from .connection import DatabaseManager, get_db_session

__all__ = [
    "Base",
    "SpiritualText",
    "Translation", 
    "Doctrine",
    "DoctrineReference",
    "Theme",
    "ThemeReference",
    "LogicalFallacy",
    "Contradiction",
    "AnalysisSession",
    "TextType",
    "Language",
    "DatabaseManager",
    "get_db_session",
]
