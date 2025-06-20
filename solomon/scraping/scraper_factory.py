"""Factory for creating appropriate scrapers based on text type."""

from typing import Dict, List, Type, Optional
from ..database.models import TextType
from ..database.connection import DatabaseManager
from .base_scraper import BaseScraper
from .bible_scraper import BibleScraper
from .quran_scraper import QuranScraper
from .hindu_texts_scraper import HinduTextsScraper
from .buddhist_texts_scraper import BuddhistTextsScraper


class ScraperFactory:
    """Factory for creating text scrapers."""
    
    _scrapers: Dict[TextType, Type[BaseScraper]] = {
        TextType.BIBLE: BibleScraper,
        TextType.QURAN: QuranScraper,
        TextType.BHAGAVAD_GITA: HinduTextsScraper,
        TextType.UPANISHADS: HinduTextsScraper,
        TextType.DHAMMAPADA: BuddhistTextsScraper,
    }
    
    @classmethod
    def create_scraper(cls, 
                      text_type: TextType, 
                      db_manager: DatabaseManager) -> BaseScraper:
        """Create a scraper for the specified text type."""
        scraper_class = cls._scrapers.get(text_type)
        
        if not scraper_class:
            raise ValueError(f"No scraper available for text type: {text_type}")
        
        return scraper_class(db_manager)
    
    @classmethod
    def get_supported_text_types(cls) -> List[TextType]:
        """Get all supported text types."""
        return list(cls._scrapers.keys())
    
    @classmethod
    def create_all_scrapers(cls, db_manager: DatabaseManager) -> Dict[TextType, BaseScraper]:
        """Create all available scrapers."""
        scrapers = {}
        
        for text_type, scraper_class in cls._scrapers.items():
            scrapers[text_type] = scraper_class(db_manager)
        
        return scrapers
    
    @classmethod
    def register_scraper(cls, 
                        text_type: TextType, 
                        scraper_class: Type[BaseScraper]) -> None:
        """Register a new scraper for a text type."""
        cls._scrapers[text_type] = scraper_class
    
    @classmethod
    def get_scraper_for_types(cls, 
                            text_types: List[TextType],
                            db_manager: DatabaseManager) -> Dict[TextType, BaseScraper]:
        """Get scrapers for specific text types."""
        scrapers = {}
        
        for text_type in text_types:
            if text_type in cls._scrapers:
                scrapers[text_type] = cls.create_scraper(text_type, db_manager)
        
        return scrapers
