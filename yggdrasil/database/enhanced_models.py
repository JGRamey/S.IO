"""Enhanced Yggdrasil database models for broad knowledge domains."""

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

class ContentType(str, Enum):
    """Extended content types for broader knowledge domains."""
    # Religious/Spiritual texts (existing)
    BIBLE = "bible"
    QURAN = "quran"
    TORAH = "torah"
    HINDU_TEXTS = "hindu_texts"
    BUDDHIST_TEXTS = "buddhist_texts"
    
    # Academic/Scientific
    RESEARCH_PAPER = "research_paper"
    SCIENTIFIC_JOURNAL = "scientific_journal"
    TEXTBOOK = "textbook"
    THESIS = "thesis"
    
    # Literature & Philosophy
    PHILOSOPHY_TEXT = "philosophy_text"
    LITERARY_WORK = "literary_work"
    POETRY = "poetry"
    ESSAY = "essay"
    
    # Reference & Knowledge
    ENCYCLOPEDIA = "encyclopedia"
    WIKIPEDIA = "wikipedia"
    MANUAL = "manual"
    DOCUMENTATION = "documentation"
    
    # Books & Publications
    FICTION_BOOK = "fiction_book"
    NON_FICTION_BOOK = "non_fiction_book"
    BIOGRAPHY = "biography"
    HISTORY_BOOK = "history_book"
    
    OTHER = "other"

class KnowledgeDomain(str, Enum):
    """Broad knowledge domains for organization."""
    RELIGION = "religion"
    PHILOSOPHY = "philosophy" 
    SCIENCE = "science"
    MATHEMATICS = "mathematics"
    HISTORY = "history"
    LITERATURE = "literature"
    ARTS = "arts"
    TECHNOLOGY = "technology"
    MEDICINE = "medicine"
    LAW = "law"
    PSYCHOLOGY = "psychology"
    EDUCATION = "education"
    POLITICS = "politics"
    ECONOMICS = "economics"
    SOCIOLOGY = "sociology"
    OTHER = "other"

class Language(str, Enum):
    """Supported languages (expanded)."""
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    GERMAN = "german"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    RUSSIAN = "russian"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    KOREAN = "korean"
    ARABIC = "arabic"
    HEBREW = "hebrew"
    SANSKRIT = "sanskrit"
    LATIN = "latin"
    GREEK = "greek"
    HINDI = "hindi"
    URDU = "urdu"
    PERSIAN = "persian"
    OTHER = "other"

class KnowledgeCategory(Base):
    """Enhanced categories for organizing knowledge across domains."""
    __tablename__ = "knowledge_categories"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[KnowledgeDomain] = mapped_column(String(50), nullable=False)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    subcategories = relationship("KnowledgeCategory", backref="parent_category", remote_side=[id])
    texts = relationship("YggdrasilText", back_populates="category")

class YggdrasilText(Base):
    """Enhanced text storage for the Yggdrasil knowledge system."""
    __tablename__ = "yggdrasil_texts"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(String(50), nullable=False)
    domain: Mapped[KnowledgeDomain] = mapped_column(String(50), nullable=False)
    language: Mapped[Language] = mapped_column(String(50), nullable=False)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    
    # Categorization
    category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id"))
    
    # Enhanced metadata
    author: Mapped[Optional[str]] = mapped_column(String(500))
    authors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))  # Multiple authors
    editor: Mapped[Optional[str]] = mapped_column(String(300))
    translator: Mapped[Optional[str]] = mapped_column(String(300))
    publisher: Mapped[Optional[str]] = mapped_column(String(300))
    publication_year: Mapped[Optional[int]] = mapped_column(Integer)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Identifiers
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    doi: Mapped[Optional[str]] = mapped_column(String(100))
    arxiv_id: Mapped[Optional[str]] = mapped_column(String(50))
    pmid: Mapped[Optional[str]] = mapped_column(String(20))  # PubMed ID
    
    # Source information
    source_url: Mapped[Optional[str]] = mapped_column(String(2000))
    source_type: Mapped[Optional[str]] = mapped_column(String(100))  # "web", "pdf", "book", etc.
    
    # Full book support
    is_full_book: Mapped[bool] = mapped_column(Boolean, default=False)
    total_pages: Mapped[Optional[int]] = mapped_column(Integer)
    chapter_count: Mapped[Optional[int]] = mapped_column(Integer)
    current_chapter: Mapped[Optional[int]] = mapped_column(Integer)
    chapter_title: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Text structure (for structured content)
    book_section: Mapped[Optional[str]] = mapped_column(String(100))
    chapter: Mapped[Optional[int]] = mapped_column(Integer)
    verse: Mapped[Optional[int]] = mapped_column(Integer)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    
    # AI and vector capabilities
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(100))
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Content analysis
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    reading_time_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Enhanced metadata as JSON
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    topics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    themes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Chunking for large texts
    chunk_sequence: Mapped[Optional[int]] = mapped_column(Integer)
    parent_text_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("yggdrasil_texts.id"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    category = relationship("KnowledgeCategory", back_populates="texts")
    child_chunks = relationship("YggdrasilText", backref="parent_text", remote_side=[id])
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_yggdrasil_domain_type", "domain", "content_type"),
        Index("idx_yggdrasil_category", "category_id"),
        Index("idx_yggdrasil_author", "author"),
        Index("idx_yggdrasil_created", "created_at"),
        Index("idx_yggdrasil_title", "title"),
        Index("idx_yggdrasil_full_text", "content", postgresql_using="gin"),
    )

# Legacy alias for backward compatibility
SpiritualText = YggdrasilText
TextType = ContentType
FieldCategory = KnowledgeCategory
