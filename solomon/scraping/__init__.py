"""Web scraping module for spiritual texts."""

from .base_scraper import BaseScraper
from .bible_scraper import BibleScraper
from .quran_scraper import QuranScraper
from .hindu_texts_scraper import HinduTextsScraper
from .buddhist_texts_scraper import BuddhistTextsScraper
from .scraper_factory import ScraperFactory
from .text_processor import TextProcessor

__all__ = [
    'BaseScraper',
    'BibleScraper', 
    'QuranScraper',
    'HinduTextsScraper',
    'BuddhistTextsScraper',
    'ScraperFactory',
    'TextProcessor'
]
