"""Enhanced book scraper for complete book import capabilities."""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
import PyPDF2
import ebooklib
from ebooklib import epub

from .base_scraper import BaseScraper, ScrapedText
from ..database.enhanced_models import ContentType, KnowledgeDomain, Language

@dataclass
class BookChapter:
    """Represents a book chapter."""
    chapter_number: int
    title: str
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None

@dataclass
class CompleteBook:
    """Represents a complete book with metadata."""
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    language: Language = Language.ENGLISH
    content_type: ContentType = ContentType.NON_FICTION_BOOK
    domain: KnowledgeDomain = KnowledgeDomain.OTHER
    chapters: List[BookChapter] = None
    full_content: Optional[str] = None
    source_url: Optional[str] = None
    total_pages: Optional[int] = None

class BookScraper(BaseScraper):
    """Enhanced scraper for complete books from various sources."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.supported_formats = ['.pdf', '.epub', '.txt', '.html']
        
    async def scrape_project_gutenberg_book(self, book_id: str) -> CompleteBook:
        """Scrape a complete book from Project Gutenberg."""
        
        base_url = f"https://www.gutenberg.org/ebooks/{book_id}"
        
        # Get book metadata
        async with self.session.get(base_url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
            title = soup.find('h1', {'itemprop': 'name'})
            title = title.get_text().strip() if title else f"Gutenberg Book {book_id}"
            
            author = soup.find('a', {'itemprop': 'creator'})
            author = author.get_text().strip() if author else "Unknown"
            
        # Get book content (plain text format)
        text_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        
        try:
            async with self.session.get(text_url) as response:
                content = await response.text()
                
                # Clean Project Gutenberg headers/footers
                content = self._clean_gutenberg_text(content)
                
                return CompleteBook(
                    title=title,
                    author=author,
                    content_type=ContentType.LITERARY_WORK,
                    domain=KnowledgeDomain.LITERATURE,
                    full_content=content,
                    source_url=text_url,
                    language=Language.ENGLISH
                )
                
        except Exception as e:
            self.logger.error(f"Error scraping Gutenberg book {book_id}: {e}")
            raise
    
    async def scrape_wikipedia_article(self, title: str) -> CompleteBook:
        """Scrape a complete Wikipedia article."""
        
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        
        async with self.session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
            # Extract main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                raise ValueError(f"Could not find content for Wikipedia article: {title}")
            
            # Remove unwanted elements
            for element in content_div.find_all(['table', 'div', 'span'], class_=re.compile('infobox|navbox|references')):
                element.decompose()
            
            # Extract text content
            paragraphs = content_div.find_all('p')
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return CompleteBook(
                title=title,
                author="Wikipedia Contributors",
                content_type=ContentType.WIKIPEDIA,
                domain=self._categorize_wikipedia_article(content),
                full_content=content,
                source_url=url,
                language=Language.ENGLISH
            )
    
    async def import_pdf_book(self, file_path: Path) -> CompleteBook:
        """Import a complete book from PDF file."""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = pdf_reader.metadata
                title = metadata.get('/Title', file_path.stem) if metadata else file_path.stem
                author = metadata.get('/Author', 'Unknown') if metadata else 'Unknown'
                
                # Extract all text
                full_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    full_content += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                
                return CompleteBook(
                    title=title,
                    author=author,
                    content_type=ContentType.NON_FICTION_BOOK,
                    domain=KnowledgeDomain.OTHER,
                    full_content=full_content,
                    total_pages=len(pdf_reader.pages),
                    source_url=f"file://{file_path}"
                )
                
        except Exception as e:
            self.logger.error(f"Error importing PDF {file_path}: {e}")
            raise
    
    async def import_epub_book(self, file_path: Path) -> CompleteBook:
        """Import a complete book from EPUB file."""
        
        try:
            book = epub.read_epub(str(file_path))
            
            # Extract metadata
            title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else file_path.stem
            authors = book.get_metadata('DC', 'creator')
            author = authors[0][0] if authors else 'Unknown'
            
            # Extract content
            chapters = []
            full_content = ""
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    chapter_text = soup.get_text()
                    full_content += f"\n\n{chapter_text}"
                    
                    chapters.append(BookChapter(
                        chapter_number=len(chapters) + 1,
                        title=f"Chapter {len(chapters) + 1}",
                        content=chapter_text
                    ))
            
            return CompleteBook(
                title=title,
                author=author,
                content_type=ContentType.NON_FICTION_BOOK,
                domain=KnowledgeDomain.OTHER,
                chapters=chapters,
                full_content=full_content,
                source_url=f"file://{file_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Error importing EPUB {file_path}: {e}")
            raise
    
    def _clean_gutenberg_text(self, content: str) -> str:
        """Clean Project Gutenberg text headers and footers."""
        
        # Remove header (everything before "*** START OF")
        start_marker = "*** START OF"
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find end of that line
            line_end = content.find('\n', start_idx)
            content = content[line_end + 1:] if line_end != -1 else content[start_idx:]
        
        # Remove footer (everything after "*** END OF")
        end_marker = "*** END OF"
        end_idx = content.find(end_marker)
        if end_idx != -1:
            content = content[:end_idx]
        
        return content.strip()
    
    def _categorize_wikipedia_article(self, content: str) -> KnowledgeDomain:
        """Categorize Wikipedia article by content analysis."""
        
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['philosophy', 'philosopher', 'philosophical']):
            return KnowledgeDomain.PHILOSOPHY
        elif any(term in content_lower for term in ['science', 'scientific', 'research', 'study']):
            return KnowledgeDomain.SCIENCE
        elif any(term in content_lower for term in ['history', 'historical', 'century', 'war']):
            return KnowledgeDomain.HISTORY
        elif any(term in content_lower for term in ['religion', 'religious', 'god', 'faith']):
            return KnowledgeDomain.RELIGION
        elif any(term in content_lower for term in ['literature', 'author', 'novel', 'poetry']):
            return KnowledgeDomain.LITERATURE
        else:
            return KnowledgeDomain.OTHER
    
    async def scrape(self) -> List[ScrapedText]:
        """Override base scrape method for book-specific scraping."""
        
        # This would be called by the scraping manager
        # For now, return empty list - specific methods should be called directly
        return []
