"""Bible scraper for various online Bible sources."""

import asyncio
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper, ScrapedText
from ..database.models import TextType, Language


class BibleScraper(BaseScraper):
    """Scraper for Bible texts from various sources."""
    
    BIBLE_GATEWAY_BASE = "https://www.biblegateway.com"
    BIBLE_HUB_BASE = "https://biblehub.com"
    
    # Bible books mapping
    BIBLE_BOOKS = {
        # Old Testament
        'genesis': 'Genesis', 'exodus': 'Exodus', 'leviticus': 'Leviticus',
        'numbers': 'Numbers', 'deuteronomy': 'Deuteronomy', 'joshua': 'Joshua',
        'judges': 'Judges', 'ruth': 'Ruth', '1samuel': '1 Samuel', '2samuel': '2 Samuel',
        '1kings': '1 Kings', '2kings': '2 Kings', '1chronicles': '1 Chronicles',
        '2chronicles': '2 Chronicles', 'ezra': 'Ezra', 'nehemiah': 'Nehemiah',
        'esther': 'Esther', 'job': 'Job', 'psalms': 'Psalms', 'proverbs': 'Proverbs',
        'ecclesiastes': 'Ecclesiastes', 'songofsolomon': 'Song of Solomon',
        'isaiah': 'Isaiah', 'jeremiah': 'Jeremiah', 'lamentations': 'Lamentations',
        'ezekiel': 'Ezekiel', 'daniel': 'Daniel', 'hosea': 'Hosea', 'joel': 'Joel',
        'amos': 'Amos', 'obadiah': 'Obadiah', 'jonah': 'Jonah', 'micah': 'Micah',
        'nahum': 'Nahum', 'habakkuk': 'Habakkuk', 'zephaniah': 'Zephaniah',
        'haggai': 'Haggai', 'zechariah': 'Zechariah', 'malachi': 'Malachi',
        
        # New Testament
        'matthew': 'Matthew', 'mark': 'Mark', 'luke': 'Luke', 'john': 'John',
        'acts': 'Acts', 'romans': 'Romans', '1corinthians': '1 Corinthians',
        '2corinthians': '2 Corinthians', 'galatians': 'Galatians', 'ephesians': 'Ephesians',
        'philippians': 'Philippians', 'colossians': 'Colossians', '1thessalonians': '1 Thessalonians',
        '2thessalonians': '2 Thessalonians', '1timothy': '1 Timothy', '2timothy': '2 Timothy',
        'titus': 'Titus', 'philemon': 'Philemon', 'hebrews': 'Hebrews', 'james': 'James',
        '1peter': '1 Peter', '2peter': '2 Peter', '1john': '1 John', '2john': '2 John',
        '3john': '3 John', 'jude': 'Jude', 'revelation': 'Revelation'
    }
    
    def get_supported_text_types(self) -> List[TextType]:
        """Get supported text types."""
        return [TextType.BIBLE]
    
    async def scrape_texts(self, 
                          books: Optional[List[str]] = None,
                          versions: Optional[List[str]] = None,
                          source: str = "bible_gateway",
                          **kwargs) -> List[ScrapedText]:
        """Scrape Bible texts."""
        if books is None:
            books = list(self.BIBLE_BOOKS.keys())[:5]  # Start with first 5 books
        
        if versions is None:
            versions = ["NIV", "ESV", "KJV"]
        
        scraped_texts = []
        
        for version in versions:
            for book in books:
                try:
                    if source == "bible_gateway":
                        texts = await self._scrape_from_bible_gateway(book, version)
                    elif source == "bible_hub":
                        texts = await self._scrape_from_bible_hub(book, version)
                    else:
                        self.logger.warning(f"Unknown source: {source}")
                        continue
                    
                    scraped_texts.extend(texts)
                    
                    # Add delay to be respectful
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {book} {version}: {e}")
                    continue
        
        return scraped_texts
    
    async def _scrape_from_bible_gateway(self, book: str, version: str) -> List[ScrapedText]:
        """Scrape from Bible Gateway."""
        book_name = self.BIBLE_BOOKS.get(book.lower(), book)
        url = f"{self.BIBLE_GATEWAY_BASE}/passage/?search={book_name}&version={version}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            # Find the passage container
            passage_div = soup.find('div', class_='passage-text')
            if not passage_div:
                self.logger.warning(f"No passage found for {book} {version}")
                return []
            
            texts = []
            
            # Extract chapters
            chapters = passage_div.find_all('div', class_='chapter-content')
            if not chapters:
                # Try alternative structure
                chapters = [passage_div]
            
            for chapter_div in chapters:
                chapter_num = self._extract_chapter_number(chapter_div)
                
                # Extract verses
                verses = chapter_div.find_all(['span', 'div'], class_=re.compile(r'verse|text'))
                
                for verse_elem in verses:
                    verse_num = self._extract_verse_number(verse_elem)
                    verse_text = self._extract_verse_text(verse_elem)
                    
                    if verse_text:
                        texts.append(ScrapedText(
                            title=f"{book_name} {chapter_num}:{verse_num}",
                            content=self.clean_text(verse_text),
                            text_type=TextType.BIBLE,
                            language=Language.ENGLISH,
                            book=book_name,
                            chapter=chapter_num,
                            verse=verse_num,
                            translator=version,
                            source_url=url,
                            metadata={
                                'version': version,
                                'source': 'Bible Gateway'
                            }
                        ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Bible Gateway {book} {version}: {e}")
            return []
    
    async def _scrape_from_bible_hub(self, book: str, version: str) -> List[ScrapedText]:
        """Scrape from Bible Hub."""
        book_name = self.BIBLE_BOOKS.get(book.lower(), book)
        
        # Bible Hub uses different URL structure
        book_abbrev = self._get_bible_hub_abbreviation(book_name)
        url = f"{self.BIBLE_HUB_BASE}/{book_abbrev}/1.htm"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find verse containers
            verse_divs = soup.find_all('div', class_='verse')
            
            for verse_div in verse_divs:
                verse_ref = verse_div.find('span', class_='reftext')
                verse_content = verse_div.find('span', class_='text')
                
                if verse_ref and verse_content:
                    # Parse reference
                    ref_text = verse_ref.get_text(strip=True)
                    book_parsed, chapter, verse = self.extract_verse_reference(ref_text)
                    
                    if book_parsed and chapter and verse:
                        texts.append(ScrapedText(
                            title=f"{book_name} {chapter}:{verse}",
                            content=self.clean_text(verse_content.get_text()),
                            text_type=TextType.BIBLE,
                            language=Language.ENGLISH,
                            book=book_name,
                            chapter=chapter,
                            verse=verse,
                            translator=version,
                            source_url=url,
                            metadata={
                                'version': version,
                                'source': 'Bible Hub'
                            }
                        ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Bible Hub {book} {version}: {e}")
            return []
    
    def _extract_chapter_number(self, element) -> int:
        """Extract chapter number from element."""
        # Look for chapter number in various places
        chapter_span = element.find('span', class_='chapternum')
        if chapter_span:
            try:
                return int(chapter_span.get_text(strip=True))
            except ValueError:
                pass
        
        # Try to find in data attributes
        if element.get('data-chapter'):
            try:
                return int(element.get('data-chapter'))
            except ValueError:
                pass
        
        return 1  # Default to chapter 1
    
    def _extract_verse_number(self, element) -> int:
        """Extract verse number from element."""
        # Look for verse number
        verse_span = element.find('sup', class_='versenum')
        if verse_span:
            try:
                verse_text = verse_span.get_text(strip=True)
                # Remove non-numeric characters
                verse_num = re.sub(r'[^\d]', '', verse_text)
                return int(verse_num) if verse_num else 1
            except ValueError:
                pass
        
        # Try data attributes
        if element.get('data-verse'):
            try:
                return int(element.get('data-verse'))
            except ValueError:
                pass
        
        return 1  # Default to verse 1
    
    def _extract_verse_text(self, element) -> str:
        """Extract verse text from element."""
        # Remove verse numbers and other markup
        text_elem = element.find('span', class_='text')
        if text_elem:
            return text_elem.get_text(strip=True)
        
        # If no specific text span, get all text but remove verse numbers
        text = element.get_text()
        # Remove verse numbers (usually at the beginning)
        text = re.sub(r'^\d+\s*', '', text)
        return text.strip()
    
    def _get_bible_hub_abbreviation(self, book_name: str) -> str:
        """Get Bible Hub abbreviation for book name."""
        abbreviations = {
            'Genesis': 'genesis',
            'Exodus': 'exodus',
            'Leviticus': 'leviticus',
            'Numbers': 'numbers',
            'Deuteronomy': 'deuteronomy',
            'Joshua': 'joshua',
            'Judges': 'judges',
            'Ruth': 'ruth',
            '1 Samuel': '1_samuel',
            '2 Samuel': '2_samuel',
            '1 Kings': '1_kings',
            '2 Kings': '2_kings',
            'Matthew': 'matthew',
            'Mark': 'mark',
            'Luke': 'luke',
            'John': 'john',
            # Add more as needed
        }
        
        return abbreviations.get(book_name, book_name.lower().replace(' ', '_'))
    
    async def scrape_specific_passage(self, 
                                    book: str, 
                                    chapter: int, 
                                    verse_start: int = 1,
                                    verse_end: Optional[int] = None,
                                    version: str = "NIV") -> List[ScrapedText]:
        """Scrape a specific Bible passage."""
        book_name = self.BIBLE_BOOKS.get(book.lower(), book)
        
        if verse_end is None:
            passage = f"{book_name} {chapter}:{verse_start}"
        else:
            passage = f"{book_name} {chapter}:{verse_start}-{verse_end}"
        
        url = f"{self.BIBLE_GATEWAY_BASE}/passage/?search={passage}&version={version}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            passage_div = soup.find('div', class_='passage-text')
            if not passage_div:
                return []
            
            texts = []
            verses = passage_div.find_all(['span', 'div'], class_=re.compile(r'verse|text'))
            
            for verse_elem in verses:
                verse_num = self._extract_verse_number(verse_elem)
                verse_text = self._extract_verse_text(verse_elem)
                
                if verse_text:
                    texts.append(ScrapedText(
                        title=f"{book_name} {chapter}:{verse_num}",
                        content=self.clean_text(verse_text),
                        text_type=TextType.BIBLE,
                        language=Language.ENGLISH,
                        book=book_name,
                        chapter=chapter,
                        verse=verse_num,
                        translator=version,
                        source_url=url,
                        metadata={
                            'version': version,
                            'source': 'Bible Gateway',
                            'passage': passage
                        }
                    ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping passage {passage} {version}: {e}")
            return []
