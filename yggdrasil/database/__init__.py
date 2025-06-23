"""Database package for Yggdrasil project."""

from .models import (
    Base,
    YggdrasilText,
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
    "YggdrasilText",
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
