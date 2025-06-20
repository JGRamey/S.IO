"""Main scraping manager for orchestrating text collection and database operations."""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from .scraper_factory import ScraperFactory
from .text_processor import TextProcessor, ProcessedText
from .base_scraper import ScrapedText
from ..database.models import TextType, SpiritualText
from ..database.connection import DatabaseManager


class ScrapingManager:
    """Manages the entire scraping workflow."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.scraper_factory = ScraperFactory()
        self.text_processor = TextProcessor()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def scrape_and_store(self, 
                             text_types: List[TextType],
                             scraping_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scrape texts and store them in the database."""
        if scraping_config is None:
            scraping_config = {}
        
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'text_types': [tt.value for tt in text_types],
            'scraped_counts': {},
            'processed_counts': {},
            'saved_counts': {},
            'errors': [],
            'processing_stats': {}
        }
        
        all_scraped_texts = []
        
        # Scrape texts for each type
        for text_type in text_types:
            try:
                self.logger.info(f"Starting scraping for {text_type.value}")
                
                # Create scraper
                scraper = self.scraper_factory.create_scraper(text_type, self.db_manager)
                
                # Get type-specific config
                type_config = scraping_config.get(text_type.value, {})
                
                # Scrape texts
                async with scraper:
                    scraped_texts = await scraper.scrape_texts(**type_config)
                
                all_scraped_texts.extend(scraped_texts)
                results['scraped_counts'][text_type.value] = len(scraped_texts)
                
                self.logger.info(f"Scraped {len(scraped_texts)} texts for {text_type.value}")
                
            except Exception as e:
                error_msg = f"Error scraping {text_type.value}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
                results['scraped_counts'][text_type.value] = 0
        
        # Process scraped texts
        self.logger.info(f"Processing {len(all_scraped_texts)} scraped texts")
        processed_texts = self.text_processor.process_texts(all_scraped_texts)
        
        # Filter by quality if specified
        min_quality = scraping_config.get('min_quality', 0.3)
        high_quality_texts = self.text_processor.filter_by_quality(processed_texts, min_quality)
        
        results['processed_counts']['total'] = len(processed_texts)
        results['processed_counts']['high_quality'] = len(high_quality_texts)
        
        # Save to database
        saved_ids = []
        for processed_text in high_quality_texts:
            try:
                # Use the original scraper to save (it has the database logic)
                text_type = processed_text.original.text_type
                scraper = self.scraper_factory.create_scraper(text_type, self.db_manager)
                
                async with scraper:
                    ids = await scraper.save_texts_to_db([processed_text.original])
                    saved_ids.extend(ids)
                
            except Exception as e:
                error_msg = f"Error saving text {processed_text.original.title}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        results['saved_counts']['total'] = len(saved_ids)
        results['processing_stats'] = self.text_processor.get_processing_stats(processed_texts)
        results['completed_at'] = datetime.utcnow().isoformat()
        
        self.logger.info(f"Scraping completed. Saved {len(saved_ids)} texts to database")
        
        return results
    
    async def scrape_specific_texts(self, 
                                  requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Scrape specific texts based on detailed requests."""
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'requests_processed': 0,
            'texts_scraped': 0,
            'texts_saved': 0,
            'errors': []
        }
        
        all_scraped_texts = []
        
        for request in requests:
            try:
                text_type = TextType(request['text_type'])
                scraper = self.scraper_factory.create_scraper(text_type, self.db_manager)
                
                async with scraper:
                    if text_type == TextType.BIBLE:
                        texts = await self._scrape_bible_request(scraper, request)
                    elif text_type == TextType.QURAN:
                        texts = await self._scrape_quran_request(scraper, request)
                    elif text_type == TextType.BHAGAVAD_GITA:
                        texts = await self._scrape_gita_request(scraper, request)
                    elif text_type == TextType.DHAMMAPADA:
                        texts = await self._scrape_dhammapada_request(scraper, request)
                    else:
                        texts = await scraper.scrape_texts(**request.get('params', {}))
                    
                    all_scraped_texts.extend(texts)
                    results['requests_processed'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing request {request}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        results['texts_scraped'] = len(all_scraped_texts)
        
        # Process and save texts
        if all_scraped_texts:
            processed_texts = self.text_processor.process_texts(all_scraped_texts)
            high_quality_texts = self.text_processor.filter_by_quality(processed_texts, 0.3)
            
            # Save to database
            for processed_text in high_quality_texts:
                try:
                    text_type = processed_text.original.text_type
                    scraper = self.scraper_factory.create_scraper(text_type, self.db_manager)
                    
                    async with scraper:
                        await scraper.save_texts_to_db([processed_text.original])
                        results['texts_saved'] += 1
                        
                except Exception as e:
                    error_msg = f"Error saving text: {str(e)}"
                    results['errors'].append(error_msg)
        
        results['completed_at'] = datetime.utcnow().isoformat()
        return results
    
    async def _scrape_bible_request(self, scraper, request: Dict[str, Any]) -> List[ScrapedText]:
        """Handle Bible-specific scraping request."""
        if 'passage' in request:
            # Specific passage request
            passage = request['passage']
            return await scraper.scrape_specific_passage(
                book=passage['book'],
                chapter=passage['chapter'],
                verse_start=passage.get('verse_start', 1),
                verse_end=passage.get('verse_end'),
                version=passage.get('version', 'NIV')
            )
        else:
            # General scraping
            return await scraper.scrape_texts(**request.get('params', {}))
    
    async def _scrape_quran_request(self, scraper, request: Dict[str, Any]) -> List[ScrapedText]:
        """Handle Quran-specific scraping request."""
        if 'verses' in request:
            # Specific verses request
            verses = request['verses']
            return await scraper.scrape_specific_verses(
                surah=verses['surah'],
                verse_start=verses.get('verse_start', 1),
                verse_end=verses.get('verse_end'),
                translations=verses.get('translations'),
                include_arabic=verses.get('include_arabic', True)
            )
        else:
            # General scraping
            return await scraper.scrape_texts(**request.get('params', {}))
    
    async def _scrape_gita_request(self, scraper, request: Dict[str, Any]) -> List[ScrapedText]:
        """Handle Bhagavad Gita-specific scraping request."""
        if 'verses' in request:
            # Specific verses request
            verses = request['verses']
            return await scraper.scrape_specific_gita_verses(
                chapter=verses['chapter'],
                verse_start=verses.get('verse_start', 1),
                verse_end=verses.get('verse_end'),
                include_sanskrit=verses.get('include_sanskrit', True),
                include_commentary=verses.get('include_commentary', False)
            )
        else:
            # General scraping
            return await scraper.scrape_texts(**request.get('params', {}))
    
    async def _scrape_dhammapada_request(self, scraper, request: Dict[str, Any]) -> List[ScrapedText]:
        """Handle Dhammapada-specific scraping request."""
        if 'verses' in request:
            # Specific verses request
            verses = request['verses']
            return await scraper.scrape_specific_dhammapada_verses(
                chapter=verses['chapter'],
                verse_start=verses.get('verse_start', 1),
                verse_end=verses.get('verse_end'),
                include_pali=verses.get('include_pali', True)
            )
        else:
            # General scraping
            return await scraper.scrape_texts(**request.get('params', {}))
    
    async def get_scraping_status(self) -> Dict[str, Any]:
        """Get current status of scraped texts in database."""
        async with self.db_manager.get_async_session() as session:
            from sqlalchemy import select, func
            
            # Count texts by type
            type_counts = {}
            for text_type in TextType:
                query = select(func.count(SpiritualText.id)).where(
                    SpiritualText.text_type == text_type
                )
                result = await session.execute(query)
                count = result.scalar() or 0
                type_counts[text_type.value] = count
            
            # Get total count
            total_query = select(func.count(SpiritualText.id))
            total_result = await session.execute(total_query)
            total_count = total_result.scalar() or 0
            
            # Get recent additions (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_query = select(func.count(SpiritualText.id)).where(
                SpiritualText.created_at >= yesterday
            )
            recent_result = await session.execute(recent_query)
            recent_count = recent_result.scalar() or 0
            
            return {
                'total_texts': total_count,
                'texts_by_type': type_counts,
                'recent_additions': recent_count,
                'supported_types': [tt.value for tt in self.scraper_factory.get_supported_text_types()],
                'status_generated_at': datetime.utcnow().isoformat()
            }
    
    def create_scraping_config(self, 
                             text_types: List[TextType],
                             **kwargs) -> Dict[str, Any]:
        """Create a scraping configuration."""
        config = {
            'min_quality': kwargs.get('min_quality', 0.3),
            'max_texts_per_type': kwargs.get('max_texts_per_type', 100)
        }
        
        # Add type-specific configurations
        for text_type in text_types:
            if text_type == TextType.BIBLE:
                config['bible'] = {
                    'books': kwargs.get('bible_books', ['genesis', 'matthew', 'john']),
                    'versions': kwargs.get('bible_versions', ['NIV', 'ESV']),
                    'source': kwargs.get('bible_source', 'bible_gateway')
                }
            elif text_type == TextType.QURAN:
                config['quran'] = {
                    'surahs': kwargs.get('quran_surahs', list(range(1, 6))),
                    'translations': kwargs.get('quran_translations', ['en.sahih']),
                    'include_arabic': kwargs.get('include_arabic', True),
                    'source': kwargs.get('quran_source', 'quran_com')
                }
            elif text_type == TextType.BHAGAVAD_GITA:
                config['bhagavad_gita'] = {
                    'text_types': [TextType.BHAGAVAD_GITA],
                    'chapters': kwargs.get('gita_chapters', list(range(1, 4))),
                    'include_sanskrit': kwargs.get('include_sanskrit', True)
                }
            elif text_type == TextType.DHAMMAPADA:
                config['dhammapada'] = {
                    'text_types': [TextType.DHAMMAPADA],
                    'chapters': kwargs.get('dhammapada_chapters', list(range(1, 4))),
                    'include_pali': kwargs.get('include_pali', True)
                }
        
        return config
    
    async def export_scraped_data(self, 
                                output_path: str,
                                text_types: Optional[List[TextType]] = None,
                                format: str = 'json') -> str:
        """Export scraped data to file."""
        import json
        
        async with self.db_manager.get_async_session() as session:
            from sqlalchemy import select
            
            query = select(SpiritualText)
            if text_types:
                query = query.where(SpiritualText.text_type.in_(text_types))
            
            result = await session.execute(query)
            texts = result.scalars().all()
            
            # Convert to dict format
            export_data = {
                'exported_at': datetime.utcnow().isoformat(),
                'total_texts': len(texts),
                'texts': []
            }
            
            for text in texts:
                export_data['texts'].append({
                    'id': str(text.id),
                    'title': text.title,
                    'content': text.content,
                    'text_type': text.text_type.value,
                    'language': text.language.value,
                    'book': text.book,
                    'chapter': text.chapter,
                    'verse': text.verse,
                    'author': text.author,
                    'translator': text.translator,
                    'source_url': text.source_url,
                    'metadata': text.metadata,
                    'created_at': text.created_at.isoformat() if text.created_at else None
                })
            
            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return str(output_file)
