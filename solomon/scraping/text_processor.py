"""Text processing utilities for scraped spiritual texts."""

import re
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .base_scraper import ScrapedText
from ..database.models import TextType, Language


@dataclass
class ProcessedText:
    """Processed spiritual text with enhanced metadata."""
    original: ScrapedText
    cleaned_content: str
    word_count: int
    themes: List[str]
    keywords: List[str]
    language_confidence: float
    quality_score: float
    processing_metadata: Dict[str, Any]


class TextProcessor:
    """Process and enhance scraped spiritual texts."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Common spiritual themes and keywords
        self.spiritual_themes = {
            'love': ['love', 'compassion', 'mercy', 'kindness', 'charity'],
            'wisdom': ['wisdom', 'knowledge', 'understanding', 'insight', 'enlightenment'],
            'faith': ['faith', 'belief', 'trust', 'devotion', 'surrender'],
            'peace': ['peace', 'tranquility', 'serenity', 'calm', 'stillness'],
            'justice': ['justice', 'righteousness', 'fairness', 'equity'],
            'forgiveness': ['forgiveness', 'pardon', 'mercy', 'grace'],
            'suffering': ['suffering', 'pain', 'sorrow', 'grief', 'tribulation'],
            'salvation': ['salvation', 'redemption', 'liberation', 'moksha', 'nirvana'],
            'prayer': ['prayer', 'meditation', 'worship', 'devotion'],
            'morality': ['good', 'evil', 'sin', 'virtue', 'ethics', 'morality'],
            'afterlife': ['heaven', 'hell', 'paradise', 'afterlife', 'eternal'],
            'divine': ['god', 'divine', 'sacred', 'holy', 'blessed'],
            'truth': ['truth', 'reality', 'dharma', 'way', 'path']
        }
        
        # Language detection patterns
        self.language_patterns = {
            Language.HEBREW: [
                r'[\u0590-\u05FF]',  # Hebrew Unicode block
                r'\b(?:אלהים|יהוה|ברוך|שלום)\b'
            ],
            Language.ARABIC: [
                r'[\u0600-\u06FF]',  # Arabic Unicode block
                r'\b(?:الله|محمد|القرآن|الإسلام)\b'
            ],
            Language.SANSKRIT: [
                r'[\u0900-\u097F]',  # Devanagari Unicode block
                r'\b(?:om|dharma|karma|moksha|brahman)\b'
            ],
            Language.GREEK: [
                r'[\u0370-\u03FF]',  # Greek Unicode block
                r'\b(?:θεός|χριστός|λόγος)\b'
            ]
        }
    
    def process_texts(self, scraped_texts: List[ScrapedText]) -> List[ProcessedText]:
        """Process a list of scraped texts."""
        processed_texts = []
        
        for text in scraped_texts:
            try:
                processed = self.process_single_text(text)
                processed_texts.append(processed)
            except Exception as e:
                self.logger.error(f"Error processing text {text.title}: {e}")
                continue
        
        return processed_texts
    
    def process_single_text(self, text: ScrapedText) -> ProcessedText:
        """Process a single scraped text."""
        # Clean the content
        cleaned_content = self.deep_clean_text(text.content)
        
        # Calculate word count
        word_count = len(cleaned_content.split())
        
        # Extract themes
        themes = self.extract_themes(cleaned_content)
        
        # Extract keywords
        keywords = self.extract_keywords(cleaned_content)
        
        # Detect language confidence
        language_confidence = self.calculate_language_confidence(cleaned_content, text.language)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(text, cleaned_content, word_count)
        
        # Create processing metadata
        processing_metadata = {
            'processed_at': datetime.utcnow().isoformat(),
            'original_length': len(text.content),
            'cleaned_length': len(cleaned_content),
            'compression_ratio': len(cleaned_content) / len(text.content) if text.content else 0,
            'has_verse_structure': self.has_verse_structure(cleaned_content),
            'estimated_reading_time': word_count / 200,  # Assuming 200 WPM
            'text_complexity': self.calculate_text_complexity(cleaned_content)
        }
        
        return ProcessedText(
            original=text,
            cleaned_content=cleaned_content,
            word_count=word_count,
            themes=themes,
            keywords=keywords,
            language_confidence=language_confidence,
            quality_score=quality_score,
            processing_metadata=processing_metadata
        )
    
    def deep_clean_text(self, text: str) -> str:
        """Perform deep cleaning of text content."""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common web artifacts
        text = re.sub(r'(?:Next|Previous|Index|Contents|Home)(?:\s*\||\s*$)', '', text, flags=re.IGNORECASE)
        
        # Remove verse numbers that are standalone
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove copyright notices
        text = re.sub(r'©.*?(?:\d{4}|\n)', '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Normalize punctuation
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        text = re.sub(r'[–—]', '-', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Clean up spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def extract_themes(self, text: str) -> List[str]:
        """Extract spiritual themes from text."""
        text_lower = text.lower()
        found_themes = []
        
        for theme, keywords in self.spiritual_themes.items():
            theme_score = 0
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                theme_score += matches
            
            # If theme appears multiple times, include it
            if theme_score >= 2:
                found_themes.append(theme)
        
        return found_themes
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their', 'mine', 'yours', 'ours', 'theirs'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def calculate_language_confidence(self, text: str, declared_language: Language) -> float:
        """Calculate confidence that text is in the declared language."""
        if not text:
            return 0.0
        
        patterns = self.language_patterns.get(declared_language, [])
        if not patterns:
            return 0.8  # Default confidence for languages without patterns
        
        total_score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                total_score += min(matches / len(text.split()) * 100, 10)
        
        # Normalize score to 0-1 range
        confidence = min(total_score / 10, 1.0)
        
        # For English, check for common English words
        if declared_language == Language.ENGLISH:
            english_indicators = ['the', 'and', 'of', 'to', 'in', 'is', 'you', 'that', 'it', 'he']
            english_count = sum(1 for word in english_indicators if word in text.lower())
            confidence = max(confidence, min(english_count / 10, 1.0))
        
        return confidence
    
    def calculate_quality_score(self, 
                              text: ScrapedText, 
                              cleaned_content: str, 
                              word_count: int) -> float:
        """Calculate a quality score for the text."""
        score = 0.0
        
        # Length score (0-30 points)
        if word_count >= 10:
            score += min(word_count / 100 * 30, 30)
        
        # Structure score (0-20 points)
        if text.chapter and text.verse:
            score += 20
        elif text.chapter or text.verse:
            score += 10
        
        # Content quality score (0-25 points)
        if cleaned_content:
            # Check for complete sentences
            sentences = re.split(r'[.!?]+', cleaned_content)
            complete_sentences = sum(1 for s in sentences if len(s.strip()) > 10)
            score += min(complete_sentences / len(sentences) * 25, 25) if sentences else 0
        
        # Metadata completeness score (0-15 points)
        metadata_fields = [text.author, text.translator, text.source_url]
        filled_fields = sum(1 for field in metadata_fields if field)
        score += (filled_fields / len(metadata_fields)) * 15
        
        # Source reliability score (0-10 points)
        reliable_sources = ['bible.com', 'biblegateway.com', 'quran.com', 'sacred-texts.com']
        if text.source_url and any(source in text.source_url for source in reliable_sources):
            score += 10
        
        return min(score / 100, 1.0)  # Normalize to 0-1
    
    def has_verse_structure(self, text: str) -> bool:
        """Check if text has verse-like structure."""
        # Look for numbered verses or poetic structure
        verse_patterns = [
            r'^\d+\.',  # Numbered verses
            r'\n\d+\s',  # Verse numbers in text
            r'\n\s*\n',  # Paragraph breaks suggesting verses
        ]
        
        for pattern in verse_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        
        return False
    
    def calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence length
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Vocabulary diversity (unique words / total words)
        unique_words = len(set(word.lower() for word in words))
        vocab_diversity = unique_words / len(words)
        
        # Combine metrics (normalized to 0-1)
        complexity = (
            min(avg_word_length / 10, 1.0) * 0.3 +
            min(avg_sentence_length / 30, 1.0) * 0.4 +
            vocab_diversity * 0.3
        )
        
        return complexity
    
    def filter_by_quality(self, 
                         processed_texts: List[ProcessedText],
                         min_quality: float = 0.5) -> List[ProcessedText]:
        """Filter texts by minimum quality score."""
        return [text for text in processed_texts if text.quality_score >= min_quality]
    
    def group_by_theme(self, processed_texts: List[ProcessedText]) -> Dict[str, List[ProcessedText]]:
        """Group texts by their primary themes."""
        theme_groups = {}
        
        for text in processed_texts:
            if text.themes:
                primary_theme = text.themes[0]  # Use first theme as primary
                if primary_theme not in theme_groups:
                    theme_groups[primary_theme] = []
                theme_groups[primary_theme].append(text)
            else:
                # Texts without themes go to 'uncategorized'
                if 'uncategorized' not in theme_groups:
                    theme_groups['uncategorized'] = []
                theme_groups['uncategorized'].append(text)
        
        return theme_groups
    
    def get_processing_stats(self, processed_texts: List[ProcessedText]) -> Dict[str, Any]:
        """Get statistics about processed texts."""
        if not processed_texts:
            return {}
        
        total_texts = len(processed_texts)
        total_words = sum(text.word_count for text in processed_texts)
        avg_quality = sum(text.quality_score for text in processed_texts) / total_texts
        
        # Theme distribution
        all_themes = []
        for text in processed_texts:
            all_themes.extend(text.themes)
        
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Language distribution
        language_counts = {}
        for text in processed_texts:
            lang = text.original.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_texts': total_texts,
            'total_words': total_words,
            'average_words_per_text': total_words / total_texts,
            'average_quality_score': avg_quality,
            'theme_distribution': theme_counts,
            'language_distribution': language_counts,
            'high_quality_texts': sum(1 for text in processed_texts if text.quality_score >= 0.8),
            'processing_date': datetime.utcnow().isoformat()
        }
