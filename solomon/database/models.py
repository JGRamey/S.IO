"""Database models for Solomon project."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, JSON,
    ForeignKey, Index, UniqueConstraint, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid


Base = declarative_base()


class TextType(str, Enum):
    """Types of spiritual texts."""
    BIBLE = "bible"
    QURAN = "quran"
    TORAH = "torah"
    UPANISHADS = "upanishads"
    BHAGAVAD_GITA = "bhagavad_gita"
    TAO_TE_CHING = "tao_te_ching"
    DHAMMAPADA = "dhammapada"
    GNOSTIC = "gnostic"
    ZOHAR = "zohar"
    OTHER = "other"


class Language(str, Enum):
    """Supported languages."""
    HEBREW = "hebrew"
    ARAMAIC = "aramaic"
    GREEK = "greek"
    LATIN = "latin"
    ARABIC = "arabic"
    SANSKRIT = "sanskrit"
    ENGLISH = "english"
    OTHER = "other"


class SpiritualText(Base):
    """Core spiritual text documents."""
    __tablename__ = "spiritual_texts"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    text_type: Mapped[TextType] = mapped_column(String(50), nullable=False)
    language: Mapped[Language] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Source information
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    manuscript_source: Mapped[Optional[str]] = mapped_column(String(500))
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Metadata
    book: Mapped[Optional[str]] = mapped_column(String(100))
    chapter: Mapped[Optional[int]] = mapped_column(Integer)
    verse: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Vector embedding
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    translations = relationship("Translation", back_populates="original_text")
    doctrines = relationship("DoctrineReference", back_populates="text")
    themes = relationship("ThemeReference", back_populates="text")
    
    __table_args__ = (
        Index("idx_spiritual_texts_type_lang", "text_type", "language"),
        Index("idx_spiritual_texts_book_chapter", "book", "chapter"),
    )


class Translation(Base):
    """Translation tracking for texts."""
    __tablename__ = "translations"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    
    # Translation details
    target_language: Mapped[Language] = mapped_column(String(50), nullable=False)
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)
    translator: Mapped[Optional[str]] = mapped_column(String(200))
    translation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Translation chain tracking
    translation_chain: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Quality metrics
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    original_text = relationship("SpiritualText", back_populates="translations")


class Doctrine(Base):
    """Religious and spiritual doctrines."""
    __tablename__ = "doctrines"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Categorization
    tradition: Mapped[str] = mapped_column(String(100))  # Christianity, Islam, etc.
    denomination: Mapped[Optional[str]] = mapped_column(String(100))  # Baptist, Sufi, etc.
    
    # Historical context
    origin_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    historical_context: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    references = relationship("DoctrineReference", back_populates="doctrine")


class DoctrineReference(Base):
    """Links between texts and doctrines."""
    __tablename__ = "doctrine_references"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    doctrine_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("doctrines.id"))
    
    # Reference details
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    context: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    text = relationship("SpiritualText", back_populates="doctrines")
    doctrine = relationship("Doctrine", back_populates="references")
    
    __table_args__ = (
        UniqueConstraint("text_id", "doctrine_id"),
    )


class Theme(Base):
    """Universal themes across spiritual traditions."""
    __tablename__ = "themes"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Theme categorization
    category: Mapped[str] = mapped_column(String(100))  # Love, Duality, Divine Good, etc.
    keywords: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    references = relationship("ThemeReference", back_populates="theme")


class ThemeReference(Base):
    """Links between texts and themes."""
    __tablename__ = "theme_references"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    theme_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("themes.id"))
    
    # Reference details
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    context: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    text = relationship("SpiritualText", back_populates="themes")
    theme = relationship("Theme", back_populates="references")
    
    __table_args__ = (
        UniqueConstraint("text_id", "theme_id"),
    )


class LogicalFallacy(Base):
    """Detected logical fallacies in texts."""
    __tablename__ = "logical_fallacies"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    
    # Fallacy details
    fallacy_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ad_hominem, strawman, etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Detection metadata
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    detected_by: Mapped[str] = mapped_column(String(100))  # agent name or method
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class Contradiction(Base):
    """Detected contradictions between texts."""
    __tablename__ = "contradictions"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text1_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    text2_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    
    # Contradiction details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    contradiction_type: Mapped[str] = mapped_column(String(100))  # doctrinal, factual, etc.
    
    # Analysis metadata
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    detected_by: Mapped[str] = mapped_column(String(100))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    text1 = relationship("SpiritualText", foreign_keys=[text1_id])
    text2 = relationship("SpiritualText", foreign_keys=[text2_id])


class AnalysisSession(Base):
    """Track analysis sessions and results."""
    __tablename__ = "analysis_sessions"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Session metadata
    session_type: Mapped[str] = mapped_column(String(50))  # theme_analysis, doctrine_search, etc.
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Results
    results: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    texts_analyzed: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Performance metrics
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
