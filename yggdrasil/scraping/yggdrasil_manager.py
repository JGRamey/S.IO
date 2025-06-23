"""Enhanced Yggdrasil scraping manager with book import and academic content support."""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from .book_scraper import BookScraper, CompleteBook
from .academic_scraper import AcademicScraper, AcademicPaper
from .scraping_manager import HybridScrapingManager
from ..database.enhanced_models import YggdrasilText, KnowledgeCategory, ContentType, KnowledgeDomain

class YggdrasilScrapingManager(HybridScrapingManager):
    """Enhanced scraping manager for the Yggdrasil knowledge system."""
    
    def __init__(self):
        super().__init__()
        self.book_scraper = None
        self.academic_scraper = None
        
    async def initialize(self):
        """Initialize enhanced scrapers."""
        await super().initialize()
        self.book_scraper = BookScraper(self.db_manager)
        self.academic_scraper = AcademicScraper(self.db_manager)
        
    async def import_complete_book(self, 
                                source: str, 
                                source_type: str = "url",
                                chunk_size: int = 5000) -> Dict[str, Any]:
        """Import a complete book and store in database."""
        
        self.logger.info(f"Starting book import from {source}")
        
        try:
            # Get book data based on source type
            if source_type == "gutenberg":
                book = await self.book_scraper.scrape_project_gutenberg_book(source)
            elif source_type == "wikipedia":
                book = await self.book_scraper.scrape_wikipedia_article(source)
            elif source_type == "pdf":
                book = await self.book_scraper.import_pdf_book(Path(source))
            elif source_type == "epub":
                book = await self.book_scraper.import_epub_book(Path(source))
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # Store in database
            result = await self._store_complete_book(book, chunk_size)
            
            self.logger.info(f"Successfully imported book: {book.title}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error importing book from {source}: {e}")
            raise
    
    async def scrape_academic_content(self, 
                                    config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape academic content based on configuration."""
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "scraped_papers": 0,
            "scraped_articles": 0,
            "errors": []
        }
        
        try:
            # Scrape arXiv papers
            if "arxiv_ids" in config:
                for arxiv_id in config["arxiv_ids"]:
                    try:
                        paper = await self.academic_scraper.scrape_arxiv_paper(arxiv_id)
                        await self._store_academic_paper(paper)
                        results["scraped_papers"] += 1
                    except Exception as e:
                        results["errors"].append(f"arXiv {arxiv_id}: {str(e)}")
            
            # Scrape Wikipedia categories
            if "wikipedia_categories" in config:
                for category in config["wikipedia_categories"]:
                    try:
                        limit = config.get("category_limit", 10)
                        articles = await self.academic_scraper.scrape_wikipedia_category(
                            category, limit
                        )
                        for article in articles:
                            await self._store_scraped_text(article)
                            results["scraped_articles"] += 1
                    except Exception as e:
                        results["errors"].append(f"Wikipedia {category}: {str(e)}")
            
            # Scrape Stanford Encyclopedia entries
            if "stanford_topics" in config:
                for topic in config["stanford_topics"]:
                    try:
                        entry = await self.academic_scraper.scrape_stanford_encyclopedia(topic)
                        if entry:
                            await self._store_scraped_text(entry)
                            results["scraped_articles"] += 1
                    except Exception as e:
                        results["errors"].append(f"Stanford {topic}: {str(e)}")
            
            results["completed_at"] = datetime.utcnow().isoformat()
            return results
            
        except Exception as e:
            results["errors"].append(f"Academic scraping error: {str(e)}")
            return results
    
    async def _store_complete_book(self, 
                                 book: CompleteBook, 
                                 chunk_size: int = 5000) -> Dict[str, Any]:
        """Store a complete book in the database."""
        
        session = self.db_manager.get_session()
        
        try:
            # Find or create category
            category = await self._get_or_create_category(book.domain, session)
            
            # Create main book entry
            main_text = YggdrasilText(
                title=book.title,
                content_type=book.content_type,
                domain=book.domain,
                language=book.language,
                content=book.full_content[:chunk_size] if len(book.full_content) > chunk_size else book.full_content,
                author=book.author,
                isbn=book.isbn,
                publisher=book.publisher,
                publication_year=book.publication_year,
                source_url=book.source_url,
                is_full_book=True,
                total_pages=book.total_pages,
                chapter_count=len(book.chapters) if book.chapters else None,
                category_id=category.id,
                word_count=len(book.full_content.split()) if book.full_content else 0,
                scraped_at=datetime.utcnow(),
                metadata={
                    "import_type": "complete_book",
                    "source_format": Path(book.source_url).suffix if book.source_url else None
                }
            )
            
            session.add(main_text)
            await session.commit()
            
            chunks_created = 0
            
            # Create chunks for large content
            if book.full_content and len(book.full_content) > chunk_size:
                chunks = self._split_text_into_chunks(book.full_content, chunk_size)
                
                for i, chunk in enumerate(chunks):
                    chunk_text = YggdrasilText(
                        title=f"{book.title} - Part {i+1}",
                        content_type=book.content_type,
                        domain=book.domain,
                        language=book.language,
                        content=chunk,
                        author=book.author,
                        source_url=book.source_url,
                        parent_text_id=main_text.id,
                        chunk_sequence=i+1,
                        category_id=category.id,
                        word_count=len(chunk.split()),
                        scraped_at=datetime.utcnow()
                    )
                    session.add(chunk_text)
                    chunks_created += 1
            
            # Store individual chapters if available
            if book.chapters:
                for chapter in book.chapters:
                    chapter_text = YggdrasilText(
                        title=f"{book.title} - {chapter.title}",
                        content_type=book.content_type,
                        domain=book.domain,
                        language=book.language,
                        content=chapter.content,
                        author=book.author,
                        source_url=book.source_url,
                        parent_text_id=main_text.id,
                        current_chapter=chapter.chapter_number,
                        chapter_title=chapter.title,
                        category_id=category.id,
                        word_count=len(chapter.content.split()),
                        scraped_at=datetime.utcnow()
                    )
                    session.add(chapter_text)
            
            await session.commit()
            
            return {
                "book_id": str(main_text.id),
                "title": book.title,
                "chunks_created": chunks_created,
                "chapters_stored": len(book.chapters) if book.chapters else 0,
                "total_words": len(book.full_content.split()) if book.full_content else 0
            }
            
        except Exception as e:
            await session.rollback()
            raise
        finally:
            session.close()
    
    async def _store_academic_paper(self, paper: AcademicPaper) -> str:
        """Store an academic paper in the database."""
        
        session = self.db_manager.get_session()
        
        try:
            category = await self._get_or_create_category(paper.domain, session)
            
            text = YggdrasilText(
                title=paper.title,
                content_type=ContentType.RESEARCH_PAPER,
                domain=paper.domain,
                language=Language.ENGLISH,
                content=paper.content,
                abstract=paper.abstract,
                authors=paper.authors,
                doi=paper.doi,
                arxiv_id=paper.arxiv_id,
                publication_date=paper.publication_date,
                keywords=paper.keywords,
                category_id=category.id,
                word_count=len(paper.content.split()),
                scraped_at=datetime.utcnow(),
                metadata={
                    "type": "academic_paper",
                    "journal": paper.journal
                }
            )
            
            session.add(text)
            await session.commit()
            
            return str(text.id)
            
        except Exception as e:
            await session.rollback()
            raise
        finally:
            session.close()
    
    async def _get_or_create_category(self, 
                                    domain: KnowledgeDomain, 
                                    session) -> KnowledgeCategory:
        """Get or create a knowledge category."""
        
        category = session.query(KnowledgeCategory).filter(
            KnowledgeCategory.domain == domain,
            KnowledgeCategory.category_name == domain.value.title()
        ).first()
        
        if not category:
            category = KnowledgeCategory(
                domain=domain,
                category_name=domain.value.title(),
                description=f"Content related to {domain.value}"
            )
            session.add(category)
            await session.commit()
        
        return category
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of approximately chunk_size characters."""
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
