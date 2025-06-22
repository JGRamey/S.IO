"""Main scraping manager for orchestrating text collection and hybrid database operations."""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import uuid

from .scraper_factory import ScraperFactory
from .text_processor import TextProcessor, ProcessedText
from .base_scraper import ScrapedText
from ..database.models import TextType, SpiritualText, FieldCategory, SubfieldCategory
from ..database.connection import db_manager, get_qdrant
from ..database.qdrant_manager import qdrant_manager
from sqlalchemy import select


class HybridScrapingManager:
    """Enhanced scraping manager for hybrid PostgreSQL + Qdrant database operations."""
    
    def __init__(self):
        self.scraper_factory = ScraperFactory()
        self.text_processor = TextProcessor()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def initialize(self):
        """Initialize the hybrid database system."""
        await db_manager.initialize_hybrid_system()
        
    async def scrape_and_store_hybrid(self, 
                                    text_types: List[TextType],
                                    scraping_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced scraping with hybrid database storage (PostgreSQL + Qdrant)."""
        if scraping_config is None:
            scraping_config = {}
        
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'text_types': [tt.value for tt in text_types],
            'scraped_counts': {},
            'processed_counts': {},
            'postgres_saved_counts': {},
            'qdrant_saved_counts': {},
            'embedding_stats': {},
            'errors': [],
            'processing_stats': {}
        }
        
        all_scraped_texts = []
        
        # Scrape texts for each type
        for text_type in text_types:
            try:
                self.logger.info(f"Starting hybrid scraping for {text_type.value}")
                
                # Create scraper
                scraper = self.scraper_factory.create_scraper(text_type, db_manager)
                if not scraper:
                    self.logger.warning(f"No scraper available for {text_type.value}")
                    continue
                
                # Configure scraper
                if text_type.value in scraping_config:
                    scraper.configure(scraping_config[text_type.value])
                
                # Scrape texts
                scraped_texts = await scraper.scrape()
                results['scraped_counts'][text_type.value] = len(scraped_texts)
                all_scraped_texts.extend(scraped_texts)
                
                self.logger.info(f"Scraped {len(scraped_texts)} texts for {text_type.value}")
                
            except Exception as e:
                error_msg = f"Error scraping {text_type.value}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Process and store in hybrid database
        if all_scraped_texts:
            processed_results = await self._process_and_store_hybrid(all_scraped_texts, results)
            results.update(processed_results)
        
        results['completed_at'] = datetime.utcnow().isoformat()
        results['total_processed'] = sum(results['processed_counts'].values())
        results['total_postgres_saved'] = sum(results['postgres_saved_counts'].values())
        results['total_qdrant_saved'] = sum(results['qdrant_saved_counts'].values())
        
        return results
    
    async def _process_and_store_hybrid(self, 
                                      scraped_texts: List[ScrapedText], 
                                      results: Dict[str, Any]) -> Dict[str, Any]:
        """Process texts and store in both PostgreSQL and Qdrant."""
        postgres_counts = {}
        qdrant_counts = {}
        processed_counts = {}
        embedding_stats = {'generated': 0, 'failed': 0, 'avg_tokens': 0}
        
        # Process texts in batches for efficiency
        batch_size = 10
        for i in range(0, len(scraped_texts), batch_size):
            batch = scraped_texts[i:i + batch_size]
            
            try:
                # Process the batch
                processed_batch = []
                for scraped_text in batch:
                    try:
                        processed_text = await self.text_processor.process(scraped_text)
                        processed_batch.append((scraped_text, processed_text))
                        
                        # Update counts
                        text_type = scraped_text.text_type.value
                        processed_counts[text_type] = processed_counts.get(text_type, 0) + 1
                        
                    except Exception as e:
                        self.logger.error(f"Error processing text: {str(e)}")
                        results['errors'].append(f"Processing error: {str(e)}")
                
                # Store in hybrid database
                postgres_saved, qdrant_saved, embed_stats = await self._store_batch_hybrid(processed_batch)
                
                # Update results
                for text_type, count in postgres_saved.items():
                    postgres_counts[text_type] = postgres_counts.get(text_type, 0) + count
                
                for text_type, count in qdrant_saved.items():
                    qdrant_counts[text_type] = qdrant_counts.get(text_type, 0) + count
                
                # Update embedding stats
                embedding_stats['generated'] += embed_stats.get('generated', 0)
                embedding_stats['failed'] += embed_stats.get('failed', 0)
                
                self.logger.info(f"Processed and stored batch {i//batch_size + 1}/{(len(scraped_texts) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                error_msg = f"Error processing batch {i//batch_size + 1}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return {
            'processed_counts': processed_counts,
            'postgres_saved_counts': postgres_counts,
            'qdrant_saved_counts': qdrant_counts,
            'embedding_stats': embedding_stats
        }
    
    async def _store_batch_hybrid(self, 
                                processed_batch: List[Tuple[ScrapedText, ProcessedText]]) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
        """Store a batch of processed texts in both PostgreSQL and Qdrant."""
        postgres_saved = {}
        qdrant_saved = {}
        embedding_stats = {'generated': 0, 'failed': 0}
        
        # Prepare data for batch operations
        spiritual_texts = []
        qdrant_batch_data = []
        
        async with db_manager.get_async_session() as session:
            for scraped_text, processed_text in processed_batch:
                try:
                    # Generate unique ID for the text
                    text_id = str(uuid.uuid4())
                    
                    # Determine field and subfield categories
                    field_category_id, subfield_category_id = await self._determine_categories(
                        session, scraped_text.text_type
                    )
                    
                    # Create SpiritualText object
                    spiritual_text = SpiritualText(
                        id=text_id,
                        title=processed_text.title,
                        text_type=scraped_text.text_type,
                        language=processed_text.language,
                        content=processed_text.content,
                        field_category_id=field_category_id,
                        subfield_category_id=subfield_category_id,
                        source_url=scraped_text.source_url,
                        manuscript_source=processed_text.manuscript_source,
                        publication_date=processed_text.publication_date,
                        author=processed_text.author,
                        book=processed_text.book,
                        chapter=processed_text.chapter,
                        verse=processed_text.verse,
                        verse_end=processed_text.verse_end,
                        token_count=processed_text.token_count,
                        chunk_sequence=processed_text.chunk_sequence,
                        qdrant_point_id=text_id,  # Use same ID for Qdrant
                        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    spiritual_texts.append(spiritual_text)
                    
                    # Prepare for Qdrant storage
                    qdrant_metadata = {
                        'title': processed_text.title,
                        'text_type': scraped_text.text_type.value,
                        'language': processed_text.language.value,
                        'book': processed_text.book,
                        'chapter': processed_text.chapter,
                        'verse': processed_text.verse,
                        'author': processed_text.author,
                        'source_url': scraped_text.source_url
                    }
                    
                    qdrant_batch_data.append((text_id, processed_text.content, qdrant_metadata))
                    
                except Exception as e:
                    self.logger.error(f"Error preparing text for storage: {str(e)}")
                    continue
            
            # Store in PostgreSQL
            try:
                session.add_all(spiritual_texts)
                await session.commit()
                
                for spiritual_text in spiritual_texts:
                    text_type = spiritual_text.text_type.value
                    postgres_saved[text_type] = postgres_saved.get(text_type, 0) + 1
                
                self.logger.info(f"Saved {len(spiritual_texts)} texts to PostgreSQL")
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error saving to PostgreSQL: {str(e)}")
        
        # Store in Qdrant
        if qdrant_batch_data:
            try:
                await qdrant_manager.add_texts_batch(qdrant_batch_data)
                
                for text_id, content, metadata in qdrant_batch_data:
                    text_type = metadata['text_type']
                    qdrant_saved[text_type] = qdrant_saved.get(text_type, 0) + 1
                    embedding_stats['generated'] += 1
                
                self.logger.info(f"Saved {len(qdrant_batch_data)} texts to Qdrant")
                
            except Exception as e:
                self.logger.error(f"Error saving to Qdrant: {str(e)}")
                embedding_stats['failed'] += len(qdrant_batch_data)
        
        return postgres_saved, qdrant_saved, embedding_stats
    
    async def _determine_categories(self, session, text_type: TextType) -> Tuple[Optional[str], Optional[str]]:
        """Determine field and subfield category IDs based on text type."""
        try:
            # Map text types to field categories
            text_type_mapping = {
                TextType.BIBLE: "Religious Books, Texts, Articles, and Other Sources",
                TextType.QURAN: "Religious Books, Texts, Articles, and Other Sources", 
                TextType.TORAH: "Religious Books, Texts, Articles, and Other Sources",
                TextType.UPANISHADS: "Religious Books, Texts, Articles, and Other Sources",
                TextType.BHAGAVAD_GITA: "Religious Books, Texts, Articles, and Other Sources",
                TextType.TAO_TE_CHING: "Religious Books, Texts, Articles, and Other Sources",
                TextType.DHAMMAPADA: "Religious Books, Texts, Articles, and Other Sources",
                TextType.GNOSTIC: "Religious Books, Texts, Articles, and Other Sources",
                TextType.ZOHAR: "Religious Books, Texts, Articles, and Other Sources",
            }
            
            # Subfield mapping
            subfield_mapping = {
                TextType.BIBLE: "Christianity (e.g., Bible, Patristic Texts)",
                TextType.QURAN: "Islam (e.g., Quran, Hadith)",
                TextType.TORAH: "Judaism (e.g., Torah, Talmud)",
                TextType.UPANISHADS: "Hinduism (e.g., Vedas, Upanishads)",
                TextType.BHAGAVAD_GITA: "Hinduism (e.g., Vedas, Upanishads)",
                TextType.TAO_TE_CHING: "Taoism (e.g., Tao Te Ching)",
                TextType.DHAMMAPADA: "Buddhism (e.g., Sutras, Tripitaka)",
                TextType.GNOSTIC: "Gnosticism",
                TextType.ZOHAR: "Judaism (e.g., Torah, Talmud)",
            }
            
            field_name = text_type_mapping.get(text_type)
            subfield_name = subfield_mapping.get(text_type)
            
            field_category_id = None
            subfield_category_id = None
            
            if field_name:
                # Get field category
                field_result = await session.execute(
                    select(FieldCategory).where(FieldCategory.field_name == field_name)
                )
                field_category = field_result.scalar_one_or_none()
                if field_category:
                    field_category_id = field_category.id
                    
                    if subfield_name:
                        # Get subfield category
                        subfield_result = await session.execute(
                            select(SubfieldCategory).where(
                                SubfieldCategory.field_id == field_category_id,
                                SubfieldCategory.subfield_name == subfield_name
                            )
                        )
                        subfield_category = subfield_result.scalar_one_or_none()
                        if subfield_category:
                            subfield_category_id = subfield_category.id
            
            return field_category_id, subfield_category_id
            
        except Exception as e:
            self.logger.error(f"Error determining categories: {str(e)}")
            return None, None


# Global instance for the enhanced scraping manager
hybrid_scraping_manager = HybridScrapingManager()
