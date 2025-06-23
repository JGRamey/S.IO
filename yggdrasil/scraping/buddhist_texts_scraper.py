"""Buddhist texts scraper for Dhammapada and other Buddhist scriptures."""

import asyncio
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

from .base_scraper import BaseScraper, ScrapedText
from ..database.models import TextType, Language


class BuddhistTextsScraper(BaseScraper):
    """Scraper for Buddhist spiritual texts."""
    
    DHAMMAPADA_BASE = "https://www.accesstoinsight.org/tipitaka/kn/dhp"
    SUTTACENTRAL_BASE = "https://suttacentral.net"
    SACRED_TEXTS_BASE = "https://www.sacred-texts.com/bud"
    
    # Dhammapada chapters
    DHAMMAPADA_CHAPTERS = {
        1: "Yamakavagga - The Twin Verses",
        2: "Appamadavagga - Heedfulness", 
        3: "Cittavagga - The Mind",
        4: "Pupphavagga - Flowers",
        5: "Balavagga - Fools",
        6: "Panditavagga - The Wise",
        7: "Arahantavagga - The Perfected Ones",
        8: "Sahassavagga - The Thousands",
        9: "Papavagga - Evil",
        10: "Dandavagga - Violence",
        11: "Jaravagga - Old Age",
        12: "Attavagga - The Self",
        13: "Lokavagga - The World",
        14: "Buddhavagga - The Buddha",
        15: "Sukhavagga - Happiness",
        16: "Piyavagga - Affection",
        17: "Kodhavagga - Anger",
        18: "Malavagga - Impurity",
        19: "Dhammatthavagga - The Righteous",
        20: "Maggavagga - The Path",
        21: "Pakinnakavagga - Miscellaneous",
        22: "Nirayavagga - The State of Woe",
        23: "Nagavagga - The Elephant",
        24: "Tanhavagga - Craving",
        25: "Bhikkhuvagga - The Monk",
        26: "Brahmanavagga - The Holy Man"
    }
    
    def get_supported_text_types(self) -> List[TextType]:
        """Get supported text types."""
        return [TextType.DHAMMAPADA]
    
    async def scrape_texts(self, 
                          text_types: Optional[List[TextType]] = None,
                          chapters: Optional[List[int]] = None,
                          include_pali: bool = True,
                          **kwargs) -> List[ScrapedText]:
        """Scrape Buddhist texts."""
        if text_types is None:
            text_types = [TextType.DHAMMAPADA]
        
        scraped_texts = []
        
        for text_type in text_types:
            try:
                if text_type == TextType.DHAMMAPADA:
                    texts = await self._scrape_dhammapada(chapters, include_pali)
                else:
                    continue
                
                scraped_texts.extend(texts)
                
                # Add delay between different text types
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping {text_type}: {e}")
                continue
        
        return scraped_texts
    
    async def _scrape_dhammapada(self, 
                               chapters: Optional[List[int]] = None,
                               include_pali: bool = True) -> List[ScrapedText]:
        """Scrape Dhammapada texts."""
        if chapters is None:
            chapters = list(range(1, 6))  # Start with first 5 chapters
        
        texts = []
        
        for chapter in chapters:
            try:
                chapter_texts = await self._scrape_dhammapada_chapter(chapter, include_pali)
                texts.extend(chapter_texts)
                
                # Add delay between chapters
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error scraping Dhammapada chapter {chapter}: {e}")
                continue
        
        return texts
    
    async def _scrape_dhammapada_chapter(self, 
                                       chapter: int,
                                       include_pali: bool) -> List[ScrapedText]:
        """Scrape a specific Dhammapada chapter."""
        chapter_name = self.DHAMMAPADA_CHAPTERS.get(chapter, f"Chapter {chapter}")
        
        # Access to Insight URL structure
        chapter_str = f"{chapter:02d}"  # Zero-padded chapter number
        url = f"{self.DHAMMAPADA_BASE}/dhp.{chapter_str}.than.html"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find verse containers
            verse_containers = soup.find_all(['p', 'div'], class_=re.compile(r'verse|dhp'))
            
            if not verse_containers:
                # Try alternative approach - look for numbered paragraphs
                verse_containers = soup.find_all('p')
            
            verse_num = 1
            
            for container in verse_containers:
                verse_text = container.get_text(strip=True)
                
                if not verse_text or len(verse_text) < 10:
                    continue
                
                # Skip navigation and header text
                if any(skip in verse_text.lower() for skip in 
                      ['next', 'previous', 'index', 'contents', 'chapter', 'translator']):
                    continue
                
                # Extract verse number if present
                verse_match = re.match(r'^(\d+)\.?\s*(.*)', verse_text)
                if verse_match:
                    extracted_verse_num = int(verse_match.group(1))
                    verse_content = verse_match.group(2)
                else:
                    extracted_verse_num = verse_num
                    verse_content = verse_text
                
                # Check if this is Pali text
                is_pali = self._is_pali_text(verse_content)
                
                if is_pali and include_pali:
                    texts.append(ScrapedText(
                        title=f"Dhammapada {chapter}.{extracted_verse_num} (Pali)",
                        content=self.clean_text(verse_content),
                        text_type=TextType.DHAMMAPADA,
                        language=Language.OTHER,  # Pali - could add to Language enum
                        book="Dhammapada",
                        chapter=chapter,
                        verse=extracted_verse_num,
                        source_url=url,
                        metadata={
                            'chapter_name': chapter_name,
                            'text_type': 'original_pali',
                            'source': 'Access to Insight'
                        }
                    ))
                elif not is_pali:
                    texts.append(ScrapedText(
                        title=f"Dhammapada {chapter}.{extracted_verse_num}",
                        content=self.clean_text(verse_content),
                        text_type=TextType.DHAMMAPADA,
                        language=Language.ENGLISH,
                        book="Dhammapada",
                        chapter=chapter,
                        verse=extracted_verse_num,
                        source_url=url,
                        metadata={
                            'chapter_name': chapter_name,
                            'source': 'Access to Insight'
                        }
                    ))
                
                verse_num += 1
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Dhammapada chapter {chapter}: {e}")
            return []
    
    async def _scrape_from_suttacentral(self, 
                                      sutta_id: str,
                                      language: str = "en") -> List[ScrapedText]:
        """Scrape from SuttaCentral."""
        url = f"{self.SUTTACENTRAL_BASE}/{sutta_id}/{language}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find the main content
            content_div = soup.find('div', class_='sutta-text') or soup.find('article')
            
            if not content_div:
                return []
            
            # Extract paragraphs
            paragraphs = content_div.find_all(['p', 'div'], class_=re.compile(r'segment|text'))
            
            if not paragraphs:
                paragraphs = content_div.find_all('p')
            
            verse_num = 1
            
            for para in paragraphs:
                text_content = para.get_text(strip=True)
                
                if not text_content or len(text_content) < 20:
                    continue
                
                # Skip navigation and metadata
                if any(skip in text_content.lower() for skip in 
                      ['next', 'previous', 'index', 'contents', 'translator', 'edition']):
                    continue
                
                texts.append(ScrapedText(
                    title=f"{sutta_id} {verse_num}",
                    content=self.clean_text(text_content),
                    text_type=TextType.DHAMMAPADA,  # Generic Buddhist text type
                    language=Language.ENGLISH if language == "en" else Language.OTHER,
                    book=sutta_id,
                    chapter=1,
                    verse=verse_num,
                    source_url=url,
                    metadata={
                        'sutta_id': sutta_id,
                        'language': language,
                        'source': 'SuttaCentral'
                    }
                ))
                
                verse_num += 1
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping SuttaCentral {sutta_id}: {e}")
            return []
    
    def _is_pali_text(self, text: str) -> bool:
        """Check if text is in Pali language."""
        # Common Pali words and patterns
        pali_indicators = [
            r'\bdhamma\b', r'\bsangha\b', r'\bbuddha\b', r'\bnibbana\b',
            r'\bdukkha\b', r'\bsamadhi\b', r'\bvipassana\b', r'\bsamsara\b',
            r'\bkarma\b', r'\bmetta\b', r'\bmudita\b', r'\bkaruna\b',
            r'\bupekkha\b', r'\bsila\b', r'\bpanna\b', r'\bsamatha\b',
            r'[aeiou]ti\b', r'[aeiou]nti\b',  # Common Pali verb endings
            r'\b[a-z]+assa\b', r'\b[a-z]+ena\b'  # Common Pali case endings
        ]
        
        text_lower = text.lower()
        matches = sum(1 for pattern in pali_indicators if re.search(pattern, text_lower))
        
        # If we find multiple Pali indicators, it's likely Pali
        return matches >= 2
    
    async def scrape_specific_dhammapada_verses(self, 
                                              chapter: int,
                                              verse_start: int = 1,
                                              verse_end: Optional[int] = None,
                                              include_pali: bool = True) -> List[ScrapedText]:
        """Scrape specific verses from Dhammapada."""
        chapter_name = self.DHAMMAPADA_CHAPTERS.get(chapter, f"Chapter {chapter}")
        
        try:
            # Scrape the whole chapter and filter
            chapter_texts = await self._scrape_dhammapada_chapter(chapter, include_pali)
            
            # Filter to requested verse range
            filtered_texts = []
            for text in chapter_texts:
                if text.verse >= verse_start and (verse_end is None or text.verse <= verse_end):
                    filtered_texts.append(text)
            
            return filtered_texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Dhammapada verses {verse_start}-{verse_end} from chapter {chapter}: {e}")
            return []
    
    async def scrape_buddhist_suttas(self, 
                                   sutta_ids: List[str],
                                   languages: Optional[List[str]] = None) -> List[ScrapedText]:
        """Scrape Buddhist suttas from SuttaCentral."""
        if languages is None:
            languages = ["en"]
        
        texts = []
        
        for sutta_id in sutta_ids:
            for language in languages:
                try:
                    sutta_texts = await self._scrape_from_suttacentral(sutta_id, language)
                    texts.extend(sutta_texts)
                    
                    # Add delay between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping sutta {sutta_id} in {language}: {e}")
                    continue
        
        return texts
    
    async def scrape_from_sacred_texts(self, 
                                     text_path: str,
                                     text_name: str) -> List[ScrapedText]:
        """Scrape Buddhist texts from Sacred Texts archive."""
        url = f"{self.SACRED_TEXTS_BASE}/{text_path}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            
            # Find the main content
            content_div = soup.find('div', class_='content') or soup.find('body')
            
            if not content_div:
                return []
            
            # Extract paragraphs
            paragraphs = content_div.find_all('p')
            
            verse_num = 1
            
            for para in paragraphs:
                text_content = para.get_text(strip=True)
                
                if not text_content or len(text_content) < 20:
                    continue
                
                # Skip navigation and header text
                if any(skip in text_content.lower() for skip in 
                      ['next', 'previous', 'index', 'contents', 'sacred-texts.com']):
                    continue
                
                texts.append(ScrapedText(
                    title=f"{text_name} {verse_num}",
                    content=self.clean_text(text_content),
                    text_type=TextType.DHAMMAPADA,  # Generic Buddhist text type
                    language=Language.ENGLISH,
                    book=text_name,
                    chapter=1,
                    verse=verse_num,
                    source_url=url,
                    metadata={
                        'text_name': text_name,
                        'source': 'Sacred Texts'
                    }
                ))
                
                verse_num += 1
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping {text_name} from Sacred Texts: {e}")
            return []
