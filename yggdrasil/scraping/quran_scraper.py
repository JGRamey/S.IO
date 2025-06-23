"""Quran scraper for various online Quran sources."""

import asyncio
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

from .base_scraper import BaseScraper, ScrapedText
from ..database.models import TextType, Language


class QuranScraper(BaseScraper):
    """Scraper for Quran texts from various sources."""
    
    QURAN_COM_BASE = "https://quran.com"
    TANZIL_BASE = "https://tanzil.net"
    
    # Surah names mapping
    SURAH_NAMES = {
        1: "Al-Fatiha", 2: "Al-Baqarah", 3: "Ali 'Imran", 4: "An-Nisa",
        5: "Al-Ma'idah", 6: "Al-An'am", 7: "Al-A'raf", 8: "Al-Anfal",
        9: "At-Tawbah", 10: "Yunus", 11: "Hud", 12: "Yusuf",
        13: "Ar-Ra'd", 14: "Ibrahim", 15: "Al-Hijr", 16: "An-Nahl",
        17: "Al-Isra", 18: "Al-Kahf", 19: "Maryam", 20: "Ta-Ha",
        21: "Al-Anbya", 22: "Al-Hajj", 23: "Al-Mu'minun", 24: "An-Nur",
        25: "Al-Furqan", 26: "Ash-Shu'ara", 27: "An-Naml", 28: "Al-Qasas",
        29: "Al-'Ankabut", 30: "Ar-Rum", 31: "Luqman", 32: "As-Sajdah",
        33: "Al-Ahzab", 34: "Saba", 35: "Fatir", 36: "Ya-Sin",
        37: "As-Saffat", 38: "Sad", 39: "Az-Zumar", 40: "Ghafir",
        41: "Fussilat", 42: "Ash-Shuraa", 43: "Az-Zukhruf", 44: "Ad-Dukhan",
        45: "Al-Jathiyah", 46: "Al-Ahqaf", 47: "Muhammad", 48: "Al-Fath",
        49: "Al-Hujurat", 50: "Qaf", 51: "Adh-Dhariyat", 52: "At-Tur",
        53: "An-Najm", 54: "Al-Qamar", 55: "Ar-Rahman", 56: "Al-Waqi'ah",
        57: "Al-Hadid", 58: "Al-Mujadila", 59: "Al-Hashr", 60: "Al-Mumtahanah",
        61: "As-Saff", 62: "Al-Jumu'ah", 63: "Al-Munafiqun", 64: "At-Taghabun",
        65: "At-Talaq", 66: "At-Tahrim", 67: "Al-Mulk", 68: "Al-Qalam",
        69: "Al-Haqqah", 70: "Al-Ma'arij", 71: "Nuh", 72: "Al-Jinn",
        73: "Al-Muzzammil", 74: "Al-Muddaththir", 75: "Al-Qiyamah", 76: "Al-Insan",
        77: "Al-Mursalat", 78: "An-Naba", 79: "An-Nazi'at", 80: "'Abasa",
        81: "At-Takwir", 82: "Al-Infitar", 83: "Al-Mutaffifin", 84: "Al-Inshiqaq",
        85: "Al-Buruj", 86: "At-Tariq", 87: "Al-A'la", 88: "Al-Ghashiyah",
        89: "Al-Fajr", 90: "Al-Balad", 91: "Ash-Shams", 92: "Al-Layl",
        93: "Ad-Duhaa", 94: "Ash-Sharh", 95: "At-Tin", 96: "Al-'Alaq",
        97: "Al-Qadr", 98: "Al-Bayyinah", 99: "Az-Zalzalah", 100: "Al-'Adiyat",
        101: "Al-Qari'ah", 102: "At-Takathur", 103: "Al-'Asr", 104: "Al-Humazah",
        105: "Al-Fil", 106: "Quraysh", 107: "Al-Ma'un", 108: "Al-Kawthar",
        109: "Al-Kafirun", 110: "An-Nasr", 111: "Al-Masad", 112: "Al-Ikhlas",
        113: "Al-Falaq", 114: "An-Nas"
    }
    
    def get_supported_text_types(self) -> List[TextType]:
        """Get supported text types."""
        return [TextType.QURAN]
    
    async def scrape_texts(self, 
                          surahs: Optional[List[int]] = None,
                          translations: Optional[List[str]] = None,
                          include_arabic: bool = True,
                          source: str = "quran_com",
                          **kwargs) -> List[ScrapedText]:
        """Scrape Quran texts."""
        if surahs is None:
            surahs = list(range(1, 6))  # Start with first 5 surahs
        
        if translations is None:
            translations = ["en.sahih", "en.pickthall", "en.yusufali"]
        
        scraped_texts = []
        
        for surah in surahs:
            try:
                if source == "quran_com":
                    texts = await self._scrape_from_quran_com(surah, translations, include_arabic)
                elif source == "tanzil":
                    texts = await self._scrape_from_tanzil(surah, translations, include_arabic)
                else:
                    self.logger.warning(f"Unknown source: {source}")
                    continue
                
                scraped_texts.extend(texts)
                
                # Add delay to be respectful
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error scraping Surah {surah}: {e}")
                continue
        
        return scraped_texts
    
    async def _scrape_from_quran_com(self, 
                                   surah: int, 
                                   translations: List[str],
                                   include_arabic: bool) -> List[ScrapedText]:
        """Scrape from Quran.com."""
        surah_name = self.SURAH_NAMES.get(surah, f"Surah {surah}")
        
        texts = []
        
        # Scrape Arabic text if requested
        if include_arabic:
            arabic_texts = await self._scrape_arabic_from_quran_com(surah)
            texts.extend(arabic_texts)
        
        # Scrape translations
        for translation in translations:
            try:
                translation_texts = await self._scrape_translation_from_quran_com(
                    surah, translation
                )
                texts.extend(translation_texts)
                
                await asyncio.sleep(0.5)  # Small delay between translations
                
            except Exception as e:
                self.logger.error(f"Error scraping translation {translation} for Surah {surah}: {e}")
                continue
        
        return texts
    
    async def _scrape_arabic_from_quran_com(self, surah: int) -> List[ScrapedText]:
        """Scrape Arabic text from Quran.com."""
        url = f"{self.QURAN_COM_BASE}/{surah}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            surah_name = self.SURAH_NAMES.get(surah, f"Surah {surah}")
            
            # Find verse containers
            verse_containers = soup.find_all('div', class_='verse-container')
            
            for container in verse_containers:
                # Extract verse number
                verse_num_elem = container.find('span', class_='verse-number')
                if not verse_num_elem:
                    continue
                
                try:
                    verse_num = int(verse_num_elem.get_text(strip=True))
                except ValueError:
                    continue
                
                # Extract Arabic text
                arabic_elem = container.find('div', class_='arabic-text')
                if arabic_elem:
                    arabic_text = arabic_elem.get_text(strip=True)
                    
                    texts.append(ScrapedText(
                        title=f"{surah_name} {surah}:{verse_num}",
                        content=self.clean_text(arabic_text),
                        text_type=TextType.QURAN,
                        language=Language.ARABIC,
                        book=surah_name,
                        chapter=surah,
                        verse=verse_num,
                        source_url=url,
                        metadata={
                            'surah_number': surah,
                            'surah_name': surah_name,
                            'source': 'Quran.com',
                            'text_type': 'original_arabic'
                        }
                    ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Arabic from Quran.com Surah {surah}: {e}")
            return []
    
    async def _scrape_translation_from_quran_com(self, 
                                               surah: int, 
                                               translation: str) -> List[ScrapedText]:
        """Scrape translation from Quran.com."""
        url = f"{self.QURAN_COM_BASE}/{surah}?translations={translation}"
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            texts = []
            surah_name = self.SURAH_NAMES.get(surah, f"Surah {surah}")
            
            # Find translation containers
            translation_containers = soup.find_all('div', class_='translation')
            
            for container in translation_containers:
                # Extract verse number from parent or sibling
                verse_container = container.find_parent('div', class_='verse-container')
                if not verse_container:
                    continue
                
                verse_num_elem = verse_container.find('span', class_='verse-number')
                if not verse_num_elem:
                    continue
                
                try:
                    verse_num = int(verse_num_elem.get_text(strip=True))
                except ValueError:
                    continue
                
                # Extract translation text
                translation_text = container.get_text(strip=True)
                
                if translation_text:
                    texts.append(ScrapedText(
                        title=f"{surah_name} {surah}:{verse_num} ({translation})",
                        content=self.clean_text(translation_text),
                        text_type=TextType.QURAN,
                        language=Language.ENGLISH,
                        book=surah_name,
                        chapter=surah,
                        verse=verse_num,
                        translator=translation,
                        source_url=url,
                        metadata={
                            'surah_number': surah,
                            'surah_name': surah_name,
                            'translation': translation,
                            'source': 'Quran.com'
                        }
                    ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping translation {translation} from Quran.com Surah {surah}: {e}")
            return []
    
    async def _scrape_from_tanzil(self, 
                                surah: int, 
                                translations: List[str],
                                include_arabic: bool) -> List[ScrapedText]:
        """Scrape from Tanzil.net."""
        # Tanzil has a different API structure
        texts = []
        surah_name = self.SURAH_NAMES.get(surah, f"Surah {surah}")
        
        # Scrape Arabic if requested
        if include_arabic:
            url = f"{self.TANZIL_BASE}/quran/{surah}"
            
            try:
                html = await self.fetch_page(url)
                soup = self.parse_html(html)
                
                # Find verse elements
                verse_elements = soup.find_all('span', class_='verse')
                
                for verse_elem in verse_elements:
                    verse_num_attr = verse_elem.get('data-verse')
                    if verse_num_attr:
                        try:
                            verse_num = int(verse_num_attr)
                            verse_text = verse_elem.get_text(strip=True)
                            
                            texts.append(ScrapedText(
                                title=f"{surah_name} {surah}:{verse_num}",
                                content=self.clean_text(verse_text),
                                text_type=TextType.QURAN,
                                language=Language.ARABIC,
                                book=surah_name,
                                chapter=surah,
                                verse=verse_num,
                                source_url=url,
                                metadata={
                                    'surah_number': surah,
                                    'surah_name': surah_name,
                                    'source': 'Tanzil.net',
                                    'text_type': 'original_arabic'
                                }
                            ))
                        except ValueError:
                            continue
                
            except Exception as e:
                self.logger.error(f"Error scraping Arabic from Tanzil Surah {surah}: {e}")
        
        return texts
    
    async def scrape_specific_verses(self, 
                                   surah: int,
                                   verse_start: int = 1,
                                   verse_end: Optional[int] = None,
                                   translations: Optional[List[str]] = None,
                                   include_arabic: bool = True) -> List[ScrapedText]:
        """Scrape specific verses from a surah."""
        if translations is None:
            translations = ["en.sahih"]
        
        surah_name = self.SURAH_NAMES.get(surah, f"Surah {surah}")
        
        if verse_end is None:
            verse_range = f"{verse_start}"
        else:
            verse_range = f"{verse_start}-{verse_end}"
        
        url = f"{self.QURAN_COM_BASE}/{surah}:{verse_range}"
        
        texts = []
        
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)
            
            # Process similar to full surah scraping but for specific verses
            verse_containers = soup.find_all('div', class_='verse-container')
            
            for container in verse_containers:
                verse_num_elem = container.find('span', class_='verse-number')
                if not verse_num_elem:
                    continue
                
                try:
                    verse_num = int(verse_num_elem.get_text(strip=True))
                    
                    # Check if verse is in requested range
                    if verse_num < verse_start:
                        continue
                    if verse_end and verse_num > verse_end:
                        continue
                    
                except ValueError:
                    continue
                
                # Extract Arabic if requested
                if include_arabic:
                    arabic_elem = container.find('div', class_='arabic-text')
                    if arabic_elem:
                        arabic_text = arabic_elem.get_text(strip=True)
                        
                        texts.append(ScrapedText(
                            title=f"{surah_name} {surah}:{verse_num}",
                            content=self.clean_text(arabic_text),
                            text_type=TextType.QURAN,
                            language=Language.ARABIC,
                            book=surah_name,
                            chapter=surah,
                            verse=verse_num,
                            source_url=url,
                            metadata={
                                'surah_number': surah,
                                'surah_name': surah_name,
                                'source': 'Quran.com',
                                'text_type': 'original_arabic',
                                'verse_range': verse_range
                            }
                        ))
                
                # Extract translations
                translation_containers = container.find_all('div', class_='translation')
                for trans_container in translation_containers:
                    translation_text = trans_container.get_text(strip=True)
                    
                    if translation_text:
                        # Try to identify which translation this is
                        translation_id = "unknown"
                        for trans in translations:
                            if trans in str(trans_container):
                                translation_id = trans
                                break
                        
                        texts.append(ScrapedText(
                            title=f"{surah_name} {surah}:{verse_num} ({translation_id})",
                            content=self.clean_text(translation_text),
                            text_type=TextType.QURAN,
                            language=Language.ENGLISH,
                            book=surah_name,
                            chapter=surah,
                            verse=verse_num,
                            translator=translation_id,
                            source_url=url,
                            metadata={
                                'surah_number': surah,
                                'surah_name': surah_name,
                                'translation': translation_id,
                                'source': 'Quran.com',
                                'verse_range': verse_range
                            }
                        ))
            
            return texts
            
        except Exception as e:
            self.logger.error(f"Error scraping verses {verse_range} from Surah {surah}: {e}")
            return []
