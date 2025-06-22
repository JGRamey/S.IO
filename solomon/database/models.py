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
    VEDAS = "vedas"
    SUTRAS = "sutras"
    TRIPITAKA = "tripitaka"
    TALMUD = "talmud"
    HADITH = "hadith"
    GURU_GRANTH_SAHIB = "guru_granth_sahib"
    ANALECTS = "analects"
    AVESTA = "avesta"
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
    CHINESE = "chinese"
    JAPANESE = "japanese"
    KOREAN = "korean"
    FRENCH = "french"
    GERMAN = "german"
    SPANISH = "spanish"
    ITALIAN = "italian"
    RUSSIAN = "russian"
    HINDI = "hindi"
    PERSIAN = "persian"
    TAMIL = "tamil"
    BENGALI = "bengali"
    PORTUGUESE = "portuguese"
    URDU = "urdu"
    PALI = "pali"
    OTHER = "other"


class FieldCategory(Base):
    """Categories and fields for organizing texts."""
    __tablename__ = "field_categories"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    subfields = relationship("SubfieldCategory", back_populates="field")
    texts = relationship("SpiritualText", back_populates="field_category")


class SubfieldCategory(Base):
    """Subfields within categories."""
    __tablename__ = "subfield_categories"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("field_categories.id"))
    subfield_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    field = relationship("FieldCategory", back_populates="subfields")
    texts = relationship("SpiritualText", back_populates="subfield_category")
    
    __table_args__ = (
        UniqueConstraint("field_id", "subfield_name"),
    )


class SpiritualText(Base):
    """Core spiritual text documents."""
    __tablename__ = "spiritual_texts"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    text_type: Mapped[TextType] = mapped_column(String(50), nullable=False)
    language: Mapped[Language] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Categorization
    field_category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("field_categories.id"))
    subfield_category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("subfield_categories.id"))
    
    # Source information
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    manuscript_source: Mapped[Optional[str]] = mapped_column(String(500))
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    author: Mapped[Optional[str]] = mapped_column(String(300))
    publisher: Mapped[Optional[str]] = mapped_column(String(300))
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    doi: Mapped[Optional[str]] = mapped_column(String(100))
    edition: Mapped[Optional[str]] = mapped_column(String(100))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Text structure metadata
    book: Mapped[Optional[str]] = mapped_column(String(100))
    chapter: Mapped[Optional[int]] = mapped_column(Integer)
    verse: Mapped[Optional[int]] = mapped_column(Integer)
    verse_end: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Vector embedding (for PostgreSQL pgvector)
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    
    # Qdrant integration
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(100))  # UUID for Qdrant point
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100))  # Model used for embedding
    
    # Content processing
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_sequence: Mapped[Optional[int]] = mapped_column(Integer)  # For chunked texts
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    field_category = relationship("FieldCategory", back_populates="texts")
    subfield_category = relationship("SubfieldCategory", back_populates="texts")
    translations = relationship("Translation", back_populates="original_text")
    doctrines = relationship("DoctrineReference", back_populates="text")
    themes = relationship("ThemeReference", back_populates="text")
    
    __table_args__ = (
        Index("idx_spiritual_texts_type_lang", "text_type", "language"),
        Index("idx_spiritual_texts_book_chapter", "book", "chapter"),
        Index("idx_spiritual_texts_field_subfield", "field_category_id", "subfield_category_id"),
        Index("idx_spiritual_texts_qdrant", "qdrant_point_id"),
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
    fallacy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(50), default='moderate')  # minor, moderate, major
    
    # AI analysis metadata
    detected_by: Mapped[str] = mapped_column(String(100), default='fallacy_detection_agent')
    analysis_version: Mapped[str] = mapped_column(String(50), default='1.0')
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class FallacyAnalysis(Base):
    """Complete fallacy analysis results for texts."""
    __tablename__ = "fallacy_analyses"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"), unique=True)
    
    # Analysis results
    total_fallacies: Mapped[int] = mapped_column(Integer, default=0)
    average_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    logical_quality_score: Mapped[float] = mapped_column(Float, default=100.0)  # 0-100
    quality_assessment: Mapped[str] = mapped_column(String(50))  # excellent, good, fair, poor, very_poor
    
    # Analysis metadata
    analysis_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    fallacy_categories: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    improvement_suggestions: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Processing details
    agent_version: Mapped[str] = mapped_column(String(50), default='1.0')
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    rag_context_used: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class DoctrineAnalysis(Base):
    """Complete doctrine analysis results for texts."""
    __tablename__ = "doctrine_analyses"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"), unique=True)
    
    # Analysis results
    total_doctrines: Mapped[int] = mapped_column(Integer, default=0)
    average_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    dominant_tradition: Mapped[Optional[str]] = mapped_column(String(100))
    doctrinal_diversity: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Detected doctrines summary
    detected_doctrines: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    tradition_distribution: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    cross_tradition_analysis: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Enhanced analysis (RAG)
    rag_enhancement: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Processing details
    agent_version: Mapped[str] = mapped_column(String(50), default='1.0')
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    rag_context_used: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class ThemeAnalysis(Base):
    """Complete theme analysis results for texts."""
    __tablename__ = "theme_analyses"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"), unique=True)
    
    # Analysis results
    total_themes: Mapped[int] = mapped_column(Integer, default=0)
    average_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    dominant_theme: Mapped[Optional[str]] = mapped_column(String(200))
    theme_diversity: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Detected themes summary
    detected_themes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    theme_categories: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    universal_themes: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Cross-tradition analysis
    cross_tradition_themes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Enhanced analysis (RAG)
    rag_enhancement: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Processing details
    agent_version: Mapped[str] = mapped_column(String(50), default='1.0')
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    rag_context_used: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class TranslationAnalysis(Base):
    """Translation quality and accuracy analysis results."""
    __tablename__ = "translation_analyses"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    translated_text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    
    # Analysis results
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    semantic_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    cultural_adaptation: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Translation issues
    detected_issues: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    improvement_suggestions: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Translation chain analysis
    translation_chain: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    chain_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Enhanced analysis (RAG)
    rag_enhancement: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Processing details
    agent_version: Mapped[str] = mapped_column(String(50), default='1.0')
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    rag_context_used: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    original_text = relationship("SpiritualText", foreign_keys=[original_text_id])
    translated_text = relationship("SpiritualText", foreign_keys=[translated_text_id])
    
    __table_args__ = (
        UniqueConstraint("original_text_id", "translated_text_id"),
    )


class TextSourceAnalysis(Base):
    """Text sourcing and authenticity analysis results."""
    __tablename__ = "text_source_analyses"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"), unique=True)
    
    # Source analysis
    authenticity_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_reliability: Mapped[float] = mapped_column(Float, default=0.0)
    manuscript_quality: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Source details
    source_chain: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    historical_context: Mapped[Optional[str]] = mapped_column(Text)
    provenance_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Quality assessment
    quality_indicators: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    concerns: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    recommendations: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Enhanced analysis (RAG)
    rag_enhancement: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Processing details
    agent_version: Mapped[str] = mapped_column(String(50), default='1.0')
    execution_time: Mapped[Optional[float]] = mapped_column(Float)
    rag_context_used: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    text = relationship("SpiritualText")


class LogicalFallacy(Base):
    """Detected logical fallacies in texts."""
    __tablename__ = "logical_fallacies"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("spiritual_texts.id"))
    
    # Fallacy details
    fallacy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(50), default='moderate')  # minor, moderate, major
    
    # AI analysis metadata
    detected_by: Mapped[str] = mapped_column(String(100), default='fallacy_detection_agent')
    analysis_version: Mapped[str] = mapped_column(String(50), default='1.0')
    
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
