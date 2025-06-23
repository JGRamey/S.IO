"""Base scraper class for spiritual texts."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from asyncio import Semaphore
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from yggdrasil.database.models import YggdrasilText, TextType, Language
from ..database.connection import DatabaseManager


@dataclass
class ScrapedText:
    """Data class for scraped spiritual text."""
    title: str
    content: str
    text_type: TextType
    language: Language
    book: Optional[str] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None
    author: Optional[str] = None
    translator: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseScraper(ABC):
    """Base class for all spiritual text scrapers with rate limiting."""
    
    def __init__(self, db_manager: DatabaseManager, max_concurrent: int = 5, request_delay: float = 1.0):
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ua = UserAgent()
        self.session = None
        
        # Rate limiting
        self.rate_limiter = Semaphore(max_concurrent)  # Max concurrent requests
        self.request_delay = request_delay  # Delay between requests
        self.max_retries = 3  # Maximum retry attempts
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            headers={'User-Agent': self.ua.random},
            timeout=30.0,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    @abstractmethod
    async def scrape_texts(self, **kwargs) -> List[ScrapedText]:
        """Scrape spiritual texts from the source."""
        pass
    
    @abstractmethod
    def get_supported_text_types(self) -> List[TextType]:
        """Get list of supported text types."""
        pass
    
    async def fetch_page(self, url: str, **kwargs) -> str:
        """Fetch a web page with error handling."""
        async with self.rate_limiter:
            await asyncio.sleep(self.request_delay)
            try:
                response = await self.session.get(url, **kwargs)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                self.logger.error(f"HTTP error fetching {url}: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                raise
    
    def parse_html(self, html: str, parser: str = 'html.parser') -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, parser)
    
    async def save_texts_to_db(self, scraped_texts: List[ScrapedText]) -> List[str]:
        """Save scraped texts to database."""
        saved_ids = []
        
        async with self.db_manager.get_async_session() as session:
            for text in scraped_texts:
                try:
                    # Check if text already exists
                    existing = await self._check_existing_text(session, text)
                    if existing:
                        self.logger.info(f"Text already exists: {text.title}")
                        continue
                    
                    # Create new spiritual text record
                    spiritual_text = YggdrasilText(
                        title=text.title,
                        content=text.content,
                        text_type=text.text_type,
                        language=text.language,
                        book=text.book,
                        chapter=text.chapter,
                        verse=text.verse,
                        author=text.author,
                        translator=text.translator,
                        source_url=text.source_url,
                        metadata=text.metadata or {}
                    )
                    
                    session.add(spiritual_text)
                    await session.flush()
                    saved_ids.append(str(spiritual_text.id))
                    
                    self.logger.info(f"Saved text: {text.title}")
                    
                except Exception as e:
                    self.logger.error(f"Error saving text {text.title}: {e}")
                    await session.rollback()
                    continue
            
            await session.commit()
        
        return saved_ids
    
    async def _check_existing_text(self, session, text: ScrapedText) -> bool:
        """Check if text already exists in database."""
        from sqlalchemy import select
        
        query = select(YggdrasilText).where(
            YggdrasilText.title == text.title,
            YggdrasilText.text_type == text.text_type,
            YggdrasilText.language == text.language
        )
        
        if text.book:
            query = query.where(YggdrasilText.book == text.book)
        if text.chapter:
            query = query.where(YggdrasilText.chapter == text.chapter)
        if text.verse:
            query = query.where(YggdrasilText.verse == text.verse)
        
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        return text.strip()
    
    def extract_verse_reference(self, text: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """Extract book, chapter, and verse from reference text."""
        import re
        
        # Pattern for "Book Chapter:Verse" format
        pattern = r'(\w+(?:\s+\w+)*)\s+(\d+):(\d+)'
        match = re.search(pattern, text)
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return book, chapter, verse
        
        return None, None, None
