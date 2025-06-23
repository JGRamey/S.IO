"""Hindu texts scraper for Bhagavad Gita, Upanishads, and other Hindu scriptures."""

import asyncio
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

from .base_scraper import BaseScraper, ScrapedText
from ..database.models import TextType, Language


class HinduTextsScraper(BaseScraper):
    """Scraper for Hindu spiritual texts."""
    
    BHAGAVAD_GITA_BASE = "https://www.holy-bhagavad-gita.org"
    UPANISHADS_BASE = "https://www.sacred-texts.com/hin"
    VEDABASE_BASE = "https://vedabase.io"
    
    # Bhagavad Gita chapters
    GITA_CHAPTERS = {
        1: "Arjuna's Dilemma", 2: "Sankhya Yoga", 3: "Karma Yoga",
        4: "Jnana Yoga", 5: "Karma Vairagya Yoga", 6: "Abhyasa Yoga",
        7: "Paramahamsa Vijnana Yoga", 8: "Aksara Parabrahma Yoga",
        9: "Raja Vidya Guhya Yoga", 10: "Vibhuti Vistara Yoga",
        11: "Visvarupa Darsana Yoga", 12: "Bhakti Yoga",
        13: "Ksetra Ksetrajna Vibhaga Yoga", 14: "Gunatraya Vibhaga Yoga",
        15: "Purusottama Yoga", 16: "Daivasura Sampad Vibhaga Yoga",
        17: "Sraddhatraya Vibhaga Yoga", 18: "Moksa Opadesa Yoga"
    }
    
    # Major Upanishads
    UPANISHADS = [
        "Isha", "Kena", "Katha", "Prashna", "Mundaka", "Mandukya",
        "Taittiriya", "Aitareya", "Chandogya", "Brihadaranyaka",
        "Svetasvatara", "Kaushitaki", "Mahanarayana"
    ]
    
    def get_supported_text_types(self) -> List[TextType]:
        """Get supported text types."""
        return [TextType.BHAGAVAD_GITA, TextType.UPANISHADS]
    
    async def scrape_texts(self, 
                          text_types: Optional[List[TextType]] = None,
                          chapters: Optional[List[int]] = None,
                          upanishads: Optional[List[str]] = None,
                          include_sanskrit: bool = True,
                          **kwargs) -> List[ScrapedText]:
        """Scrape Hindu texts."""
        if text_types is None:
            text_types = [TextType.BHAGAVAD_GITA, TextType.UPANISHADS]
        
        scraped_texts = []
        
        for text_type in text_types:
            try:
                if text_type == TextType.BHAGAVAD_GITA:
                    texts = await self._scrape_bhagavad_gita(chapters, include_sanskrit)
                elif text_type == TextType.UPANISHADS:
                    texts = await self._scrape_upanishads(upanishads, include_sanskrit)
                else:
                    continue
                
                scraped_texts.extend(texts)
                
                # Add delay between different text types
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping {text_type}: {e}")
                continue
        
        return scraped_texts
    
    async def _scrape_bhagavad_gita(self, 
                                  chapters: Optional[List[int]] = None,
                                  include_sanskrit: bool = True) -> List[ScrapedText]:
        """Scrape Bhagavad Gita texts."""
        if chapters is None:
            chapters = list(range(1, 6))  # Start with first 5 chapters
        
        texts = []
        
        for chapter in chapters:
            try:
                chapter_texts = await self._scrape_gita_chapter(chapter, include_sanskrit)
                texts.extend(chapter_texts)
                
                # Add delay between chapters
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error scraping Gita chapter {chapter}: {e}")
                continue
        
        return texts
    
    async def _scrape_gita_chapter(self, 
                                 chapter: int,
                                 include_sanskrit: bool) -> List[ScrapedText]:
        """Scrape a specific Bhagavad Gita chapter."""
        chapter_name = self.GITA_CHAPTERS.get(chapter, f"Chapter {chapter}")
        url = f"{self.BHAGAVAD_GITA_BASE}/chapter/{chapter}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find verse containers
            verse_containers = soup.find_all('div', class_=['verse', 'sloka'])
            
            if not verse_containers:
                # Try alternative selectors
                verse_containers = soup.find_all('div', id=re.compile(r'verse|sloka'))
            
            for container in verse_containers:
                verse_num = self._extract_gita_verse_number(container)
                if not verse_num:
                    continue
                
                # Extract Sanskrit if available and requested
                if include_sanskrit:
                    sanskrit_text = self._extract_sanskrit_text(container)
                    if sanskrit_text:
                        texts.append(ScrapedText(
                            title=f"Bhagavad Gita {chapter}.{verse_num} (Sanskrit)",
                            content=self.clean_text(sanskrit_text),
                            text_type=TextType.BHAGAVAD_GITA,
                            language=Language.SANSKRIT,
                            book="Bhagavad Gita",
                            chapter=chapter,
                            verse=verse_num,
                            source_url=url,
                            metadata={
                                'chapter_name': chapter_name,
                                'text_type': 'original_sanskrit',
                                'source': 'Holy Bhagavad Gita'
                            }
                        ))
                
                # Extract English translation
                english_text = self._extract_english_translation(container)
                if english_text:
                    texts.append(ScrapedText(
                        title=f"Bhagavad Gita {chapter}.{verse_num}",
                        content=self.clean_text(english_text),
                        text_type=TextType.BHAGAVAD_GITA,
                        language=Language.ENGLISH,
                        book="Bhagavad Gita",
                        chapter=chapter,
                        verse=verse_num,
                        source_url=url,
                        metadata={
                            'chapter_name': chapter_name,
                            'source': 'Holy Bhagavad Gita'
                        }
                    ))
                
                # Extract commentary if available
                commentary = self._extract_commentary(container)
                if commentary:
                    texts.append(ScrapedText(
                        title=f"Bhagavad Gita {chapter}.{verse_num} (Commentary)",
                        content=self.clean_text(commentary),
                        text_type=TextType.BHAGAVAD_GITA,
                        language=Language.ENGLISH,
                        book="Bhagavad Gita",
                        chapter=chapter,
                        verse=verse_num,
                        source_url=url,
                        metadata={
                            'chapter_name': chapter_name,
                            'text_type': 'commentary',
                            'source': 'Holy Bhagavad Gita'
                        }
                    ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Gita chapter {chapter}: {e}")
            return []
    
    async def _scrape_upanishads(self, 
                               upanishads: Optional[List[str]] = None,
                               include_sanskrit: bool = True) -> List[ScrapedText]:
        """Scrape Upanishads texts."""
        if upanishads is None:
            upanishads = self.UPANISHADS[:3]  # Start with first 3 Upanishads
        
        texts = []
        
        for upanishad in upanishads:
            try:
                upanishad_texts = await self._scrape_single_upanishad(upanishad, include_sanskrit)
                texts.extend(upanishad_texts)
                
                # Add delay between Upanishads
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error scraping Upanishad {upanishad}: {e}")
                continue
        
        return texts
    
    async def _scrape_single_upanishad(self, 
                                     upanishad: str,
                                     include_sanskrit: bool) -> List[ScrapedText]:
        """Scrape a single Upanishad."""
        # Sacred-texts.com URL structure
        upanishad_lower = upanishad.lower()
        url = f"{self.UPANISHADS_BASE}/upan/{upanishad_lower}.htm"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find the main content
            content_div = soup.find('div', class_='content') or soup.find('body')
            
            if not content_div:
                return []
            
            # Extract paragraphs and verses
            paragraphs = content_div.find_all(['p', 'div'], class_=re.compile(r'verse|mantra|text'))
            
            if not paragraphs:
                # Fallback to all paragraphs
                paragraphs = content_div.find_all('p')
            
            verse_num = 1
            
            for para in paragraphs:
                text_content = para.get_text(strip=True)
                
                if not text_content or len(text_content) < 20:
                    continue
                
                # Skip navigation and header text
                if any(skip in text_content.lower() for skip in ['next', 'previous', 'index', 'contents']):
                    continue
                
                # Determine if this is Sanskrit or English
                is_sanskrit = self._is_sanskrit_text(text_content)
                
                if is_sanskrit and include_sanskrit:
                    texts.append(ScrapedText(
                        title=f"{upanishad} Upanishad {verse_num} (Sanskrit)",
                        content=self.clean_text(text_content),
                        text_type=TextType.UPANISHADS,
                        language=Language.SANSKRIT,
                        book=f"{upanishad} Upanishad",
                        chapter=1,
                        verse=verse_num,
                        source_url=url,
                        metadata={
                            'upanishad_name': upanishad,
                            'text_type': 'original_sanskrit',
                            'source': 'Sacred Texts'
                        }
                    ))
                elif not is_sanskrit:
                    texts.append(ScrapedText(
                        title=f"{upanishad} Upanishad {verse_num}",
                        content=self.clean_text(text_content),
                        text_type=TextType.UPANISHADS,
                        language=Language.ENGLISH,
                        book=f"{upanishad} Upanishad",
                        chapter=1,
                        verse=verse_num,
                        source_url=url,
                        metadata={
                            'upanishad_name': upanishad,
                            'source': 'Sacred Texts'
                        }
                    ))
                
                verse_num += 1
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping {upanishad} Upanishad: {e}")
            return []
    
    def _extract_gita_verse_number(self, container) -> Optional[int]:
        """Extract verse number from Gita container."""
        # Look for verse number in various places
        verse_elem = container.find(['span', 'div'], class_=re.compile(r'verse.*num|num.*verse'))
        
        if verse_elem:
            verse_text = verse_elem.get_text(strip=True)
            # Extract number from text like "Verse 1" or "1"
            match = re.search(r'(\d+)', verse_text)
            if match:
                return int(match.group(1))
        
        # Try data attributes
        if container.get('data-verse'):
            try:
                return int(container.get('data-verse'))
            except ValueError:
                pass
        
        # Try ID attribute
        if container.get('id'):
            match = re.search(r'verse.*?(\d+)', container.get('id'))
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_sanskrit_text(self, container) -> Optional[str]:
        """Extract Sanskrit text from container."""
        # Look for Sanskrit text in various elements
        sanskrit_elem = container.find(['div', 'span', 'p'], class_=re.compile(r'sanskrit|devanagari'))
        
        if sanskrit_elem:
            return sanskrit_elem.get_text(strip=True)
        
        # If no specific Sanskrit element, check if the main text is Sanskrit
        main_text = container.get_text(strip=True)
        if self._is_sanskrit_text(main_text):
            return main_text
        
        return None
    
    def _extract_english_translation(self, container) -> Optional[str]:
        """Extract English translation from container."""
        # Look for translation elements
        trans_elem = container.find(['div', 'span', 'p'], class_=re.compile(r'translation|english'))
        
        if trans_elem:
            return trans_elem.get_text(strip=True)
        
        # If no specific translation element, get main text if it's English
        main_text = container.get_text(strip=True)
        if not self._is_sanskrit_text(main_text):
            return main_text
        
        return None
    
    def _extract_commentary(self, container) -> Optional[str]:
        """Extract commentary from container."""
        commentary_elem = container.find(['div', 'span', 'p'], class_=re.compile(r'commentary|purport|explanation'))
        
        if commentary_elem:
            return commentary_elem.get_text(strip=True)
        
        return None
    
    def _is_sanskrit_text(self, text: str) -> bool:
        """Check if text is in Sanskrit (Devanagari script)."""
        # Check for Devanagari Unicode range
        devanagari_count = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        
        # If more than 10% of characters are Devanagari, consider it Sanskrit
        if len(text) > 0 and devanagari_count / len(text) > 0.1:
            return True
        
        # Also check for common Sanskrit transliteration patterns
        sanskrit_patterns = [
            r'[aeiou]m\b',  # Common Sanskrit endings
            r'[kg]h[aeiou]',  # Aspirated consonants
            r'[td]h[aeiou]',
            r'[pb]h[aeiou]',
            r'[rl]i\b',
            r'[aeiou]h\b'
        ]
        
        pattern_matches = sum(1 for pattern in sanskrit_patterns if re.search(pattern, text.lower()))
        
        return pattern_matches >= 2
    
    async def scrape_specific_gita_verses(self, 
                                        chapter: int,
                                        verse_start: int = 1,
                                        verse_end: Optional[int] = None,
                                        include_sanskrit: bool = True,
                                        include_commentary: bool = False) -> List[ScrapedText]:
        """Scrape specific verses from Bhagavad Gita."""
        chapter_name = self.GITA_CHAPTERS.get(chapter, f"Chapter {chapter}")
        
        if verse_end is None:
            verse_range = f"{verse_start}"
        else:
            verse_range = f"{verse_start}-{verse_end}"
        
        url = f"{self.BHAGAVAD_GITA_BASE}/chapter/{chapter}/verse/{verse_start}"
        
        try:
            # For now, scrape the whole chapter and filter
            chapter_texts = await self._scrape_gita_chapter(chapter, include_sanskrit)
            
            # Filter to requested verse range
            filtered_texts = []
            for text in chapter_texts:
                if text.verse >= verse_start and (verse_end is None or text.verse <= verse_end):
                    if not include_commentary and 'commentary' in text.metadata.get('text_type', ''):
                        continue
                    filtered_texts.append(text)
            
            return filtered_texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Gita verses {verse_range} from chapter {chapter}: {e}")
            return []
