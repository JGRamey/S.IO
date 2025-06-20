"""Theme recognition agent for identifying universal themes in spiritual texts."""

import json
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from datetime import datetime

from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from solomon.config import settings
from .base import BaseAgent, AgentResult


class UniversalTheme(BaseModel):
    """Structure for universal spiritual themes."""
    name: str
    description: str
    keywords: List[str]
    related_concepts: List[str]
    traditions: List[str]  # Which traditions commonly express this theme


class DetectedTheme(BaseModel):
    """Structure for detected themes in text."""
    theme_name: str
    confidence_score: float
    text_excerpts: List[str]
    explanation: str
    cross_references: List[str]  # Similar themes in other traditions


class ThemeRecognitionAgent(BaseAgent):
    """Agent for recognizing universal themes across spiritual traditions."""
    
    UNIVERSAL_THEMES = {
        "divine_love": UniversalTheme(
            name="Divine Love",
            description="The concept of unconditional, transcendent love from the divine",
            keywords=["love", "agape", "rahman", "metta", "compassion", "mercy", "grace"],
            related_concepts=["forgiveness", "kindness", "benevolence", "charity"],
            traditions=["Christianity", "Islam", "Buddhism", "Hinduism", "Judaism"]
        ),
        "unity_oneness": UniversalTheme(
            name="Unity/Oneness",
            description="The fundamental unity of all existence with the divine",
            keywords=["unity", "oneness", "tawhid", "brahman", "atman", "shema", "non-duality"],
            related_concepts=["interconnectedness", "wholeness", "integration", "harmony"],
            traditions=["Islam", "Hinduism", "Judaism", "Sufism", "Advaita"]
        ),
        "spiritual_purification": UniversalTheme(
            name="Spiritual Purification",
            description="The process of cleansing and purifying the soul",
            keywords=["purification", "cleansing", "sanctification", "tazkiyah", "shuddhi"],
            related_concepts=["repentance", "atonement", "karma", "sin", "redemption"],
            traditions=["Christianity", "Islam", "Hinduism", "Judaism", "Buddhism"]
        ),
        "divine_wisdom": UniversalTheme(
            name="Divine Wisdom",
            description="Sacred knowledge and understanding from divine sources",
            keywords=["wisdom", "sophia", "hikmah", "prajna", "gnosis", "da'at"],
            related_concepts=["knowledge", "understanding", "insight", "revelation", "enlightenment"],
            traditions=["Christianity", "Islam", "Buddhism", "Hinduism", "Judaism", "Gnosticism"]
        ),
        "moral_duality": UniversalTheme(
            name="Moral Duality",
            description="The struggle between good and evil, light and darkness",
            keywords=["good", "evil", "light", "darkness", "righteousness", "sin", "virtue", "vice"],
            related_concepts=["temptation", "choice", "free will", "moral struggle"],
            traditions=["Christianity", "Islam", "Zoroastrianism", "Judaism", "Manichaeism"]
        ),
        "divine_justice": UniversalTheme(
            name="Divine Justice",
            description="The concept of divine judgment and cosmic justice",
            keywords=["justice", "judgment", "righteousness", "fairness", "balance", "karma"],
            related_concepts=["accountability", "consequences", "retribution", "reward"],
            traditions=["Christianity", "Islam", "Judaism", "Hinduism", "Buddhism"]
        ),
        "spiritual_journey": UniversalTheme(
            name="Spiritual Journey",
            description="The path of spiritual development and transformation",
            keywords=["path", "journey", "way", "tariqah", "marga", "dao", "derech"],
            related_concepts=["pilgrimage", "quest", "seeking", "progress", "stages"],
            traditions=["Islam", "Christianity", "Hinduism", "Buddhism", "Taoism", "Judaism"]
        ),
        "divine_transcendence": UniversalTheme(
            name="Divine Transcendence",
            description="The concept of divine reality beyond ordinary experience",
            keywords=["transcendent", "beyond", "ineffable", "mystery", "unknowable", "absolute"],
            related_concepts=["mystical", "sublime", "infinite", "eternal", "sacred"],
            traditions=["Christianity", "Islam", "Judaism", "Hinduism", "Buddhism"]
        ),
        "compassionate_service": UniversalTheme(
            name="Compassionate Service",
            description="The call to serve others with compassion and selflessness",
            keywords=["service", "seva", "khidmah", "charity", "helping", "giving", "sacrifice"],
            related_concepts=["altruism", "selflessness", "generosity", "care", "ministry"],
            traditions=["Christianity", "Islam", "Hinduism", "Buddhism", "Judaism", "Sikhism"]
        ),
        "inner_peace": UniversalTheme(
            name="Inner Peace",
            description="The attainment of spiritual tranquility and serenity",
            keywords=["peace", "tranquility", "serenity", "stillness", "calm", "equanimity"],
            related_concepts=["meditation", "contemplation", "silence", "rest", "harmony"],
            traditions=["Buddhism", "Christianity", "Islam", "Hinduism", "Taoism"]
        )
    }
    
    def __init__(self):
        super().__init__(
            name="theme_recognition",
            description="Recognizes universal themes across spiritual traditions"
        )
        
        # Initialize sentence transformer for semantic similarity
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute theme recognition on provided text."""
        try:
            text = input_data.get("text", "")
            text_id = input_data.get("text_id")
            tradition = input_data.get("tradition", "")
            language = input_data.get("language", "english")
            
            if not text:
                return self._create_result(
                    success=False,
                    error="Text parameter is required"
                )
            
            # Detect themes using multiple methods
            detected_themes = await self._detect_themes(text, tradition, language)
            
            # Find cross-references with other traditions
            cross_references = await self._find_cross_references(detected_themes, tradition)
            
            # Score and rank themes
            ranked_themes = self._rank_themes(detected_themes)
            
            return self._create_result(
                success=True,
                data={
                    "text_id": text_id,
                    "tradition": tradition,
                    "themes_detected": len(ranked_themes),
                    "themes": [t.dict() for t in ranked_themes],
                    "cross_references": cross_references,
                    "analysis_summary": self._create_summary(ranked_themes)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Theme recognition failed: {e}")
            return self._create_result(
                success=False,
                error=str(e)
            )
    
    async def _detect_themes(
        self, 
        text: str, 
        tradition: str = "", 
        language: str = "english"
    ) -> List[DetectedTheme]:
        """Detect themes using multiple detection methods."""
        detected = []
        
        # Method 1: Keyword-based detection
        keyword_themes = self._detect_by_keywords(text)
        detected.extend(keyword_themes)
        
        # Method 2: Semantic similarity (if sentence model available)
        if self.sentence_model:
            semantic_themes = self._detect_by_semantics(text)
            detected.extend(semantic_themes)
        
        # Method 3: LLM-based detection
        llm_themes = await self._detect_by_llm(text, tradition, language)
        detected.extend(llm_themes)
        
        # Merge and deduplicate
        return self._merge_theme_detections(detected)
    
    def _detect_by_keywords(self, text: str) -> List[DetectedTheme]:
        """Detect themes using keyword matching."""
        detected = []
        text_lower = text.lower()
        
        for theme_key, theme_info in self.UNIVERSAL_THEMES.items():
            matched_keywords = []
            matched_excerpts = []
            
            # Check for keywords and related concepts
            all_keywords = theme_info.keywords + theme_info.related_concepts
            
            for keyword in all_keywords:
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)
                    # Find sentences containing the keyword
                    sentences = self._split_into_sentences(text)
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            matched_excerpts.append(sentence)
            
            if matched_keywords:
                confidence = min(len(matched_keywords) * 0.2, 0.8)  # Cap at 0.8
                
                detected.append(DetectedTheme(
                    theme_name=theme_info.name,
                    confidence_score=confidence,
                    text_excerpts=matched_excerpts[:3],  # Limit excerpts
                    explanation=f"Keywords found: {', '.join(matched_keywords)}",
                    cross_references=[]
                ))
        
        return detected
    
    def _detect_by_semantics(self, text: str) -> List[DetectedTheme]:
        """Detect themes using semantic similarity."""
        if not self.sentence_model:
            return []
        
        detected = []
        
        try:
            # Split text into sentences
            sentences = self._split_into_sentences(text)
            if not sentences:
                return []
            
            # Get embeddings for text sentences
            sentence_embeddings = self.sentence_model.encode(sentences)
            
            # Check each theme
            for theme_key, theme_info in self.UNIVERSAL_THEMES.items():
                # Create theme description for embedding
                theme_text = f"{theme_info.name}: {theme_info.description}"
                theme_embedding = self.sentence_model.encode([theme_text])
                
                # Calculate similarities
                similarities = cosine_similarity(sentence_embeddings, theme_embedding).flatten()
                
                # Find high-similarity sentences
                high_sim_indices = np.where(similarities > 0.3)[0]
                
                if len(high_sim_indices) > 0:
                    max_similarity = similarities.max()
                    relevant_sentences = [sentences[i] for i in high_sim_indices[:3]]
                    
                    detected.append(DetectedTheme(
                        theme_name=theme_info.name,
                        confidence_score=float(max_similarity),
                        text_excerpts=relevant_sentences,
                        explanation=f"Semantic similarity: {max_similarity:.2f}",
                        cross_references=[]
                    ))
            
        except Exception as e:
            self.logger.error(f"Semantic theme detection failed: {e}")
        
        return detected
    
    async def _detect_by_llm(
        self, 
        text: str, 
        tradition: str = "", 
        language: str = "english"
    ) -> List[DetectedTheme]:
        """Detect themes using LLM analysis."""
        try:
            system_prompt = f"""You are an expert in comparative religion and spiritual traditions. Your task is to identify universal spiritual themes in the provided text.

Focus on these universal themes that appear across traditions:
1. Divine Love - Unconditional love from the divine
2. Unity/Oneness - Fundamental unity with the divine
3. Spiritual Purification - Cleansing of the soul
4. Divine Wisdom - Sacred knowledge and understanding
5. Moral Duality - Struggle between good and evil
6. Divine Justice - Cosmic justice and judgment
7. Spiritual Journey - Path of spiritual development
8. Divine Transcendence - Divine reality beyond ordinary experience
9. Compassionate Service - Call to serve others
10. Inner Peace - Spiritual tranquility and serenity

For each theme you identify, provide:
- The theme name
- Specific text excerpts that express this theme
- Confidence score (0.0 to 1.0)
- Brief explanation of how the text expresses this theme

Respond in JSON format."""
            
            tradition_context = f"This text is from the {tradition} tradition." if tradition else ""
            
            analysis_prompt = f"""Identify universal spiritual themes in this text:

{tradition_context}
Language: {language}

Text to analyze:
{text}

Identify themes and respond in this JSON format:
{{
  "themes": [
    {{
      "name": "theme_name",
      "excerpts": ["relevant text excerpt 1", "relevant text excerpt 2"],
      "confidence": 0.8,
      "explanation": "how this theme is expressed in the text"
    }}
  ]
}}"""
            
            response = await self._analyze_text(text, analysis_prompt, system_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                detected = []
                
                for theme_data in result.get("themes", []):
                    theme_name = theme_data.get("name", "")
                    
                    # Map to our standard theme names
                    mapped_theme = self._map_theme_name(theme_name)
                    if mapped_theme:
                        detected.append(DetectedTheme(
                            theme_name=mapped_theme,
                            confidence_score=theme_data.get("confidence", 0.5),
                            text_excerpts=theme_data.get("excerpts", []),
                            explanation=theme_data.get("explanation", ""),
                            cross_references=[]
                        ))
                
                return detected
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse LLM JSON response")
                return self._parse_llm_text_response(response)
                
        except Exception as e:
            self.logger.error(f"LLM theme detection failed: {e}")
            return []
    
    def _map_theme_name(self, llm_theme_name: str) -> Optional[str]:
        """Map LLM-generated theme name to our standard themes."""
        llm_lower = llm_theme_name.lower()
        
        for theme_key, theme_info in self.UNIVERSAL_THEMES.items():
            if (theme_info.name.lower() in llm_lower or 
                llm_lower in theme_info.name.lower()):
                return theme_info.name
        
        # Check for keyword matches
        for theme_key, theme_info in self.UNIVERSAL_THEMES.items():
            for keyword in theme_info.keywords:
                if keyword.lower() in llm_lower:
                    return theme_info.name
        
        return None
    
    def _parse_llm_text_response(self, response: str) -> List[DetectedTheme]:
        """Parse non-JSON LLM response for themes."""
        detected = []
        
        for theme_key, theme_info in self.UNIVERSAL_THEMES.items():
            if theme_info.name.lower() in response.lower():
                # Extract context around the theme mention
                lines = response.split('\n')
                relevant_lines = []
                
                for line in lines:
                    if theme_info.name.lower() in line.lower():
                        relevant_lines.append(line.strip())
                
                if relevant_lines:
                    detected.append(DetectedTheme(
                        theme_name=theme_info.name,
                        confidence_score=0.4,
                        text_excerpts=relevant_lines[:2],
                        explanation=f"LLM identified {theme_info.name}",
                        cross_references=[]
                    ))
        
        return detected
    
    async def _find_cross_references(
        self, 
        detected_themes: List[DetectedTheme], 
        current_tradition: str
    ) -> Dict[str, List[str]]:
        """Find cross-references to similar themes in other traditions."""
        cross_refs = {}
        
        for theme in detected_themes:
            # Find the theme info
            theme_info = None
            for theme_key, info in self.UNIVERSAL_THEMES.items():
                if info.name == theme.theme_name:
                    theme_info = info
                    break
            
            if theme_info:
                # Find other traditions that express this theme
                other_traditions = [t for t in theme_info.traditions if t != current_tradition]
                cross_refs[theme.theme_name] = other_traditions
        
        return cross_refs
    
    def _merge_theme_detections(self, detected: List[DetectedTheme]) -> List[DetectedTheme]:
        """Merge similar theme detections."""
        theme_groups = defaultdict(list)
        
        # Group by theme name
        for theme in detected:
            theme_groups[theme.theme_name].append(theme)
        
        merged = []
        for theme_name, themes in theme_groups.items():
            if len(themes) == 1:
                merged.append(themes[0])
            else:
                # Merge multiple detections of the same theme
                best_theme = max(themes, key=lambda t: t.confidence_score)
                
                # Combine excerpts and explanations
                all_excerpts = []
                all_explanations = []
                
                for theme in themes:
                    all_excerpts.extend(theme.text_excerpts)
                    all_explanations.append(theme.explanation)
                
                # Remove duplicates and limit
                unique_excerpts = list(dict.fromkeys(all_excerpts))[:5]
                combined_explanation = "; ".join(set(all_explanations))
                
                merged_theme = DetectedTheme(
                    theme_name=theme_name,
                    confidence_score=best_theme.confidence_score,
                    text_excerpts=unique_excerpts,
                    explanation=combined_explanation,
                    cross_references=best_theme.cross_references
                )
                merged.append(merged_theme)
        
        return merged
    
    def _rank_themes(self, themes: List[DetectedTheme]) -> List[DetectedTheme]:
        """Rank themes by confidence score and relevance."""
        return sorted(themes, key=lambda t: t.confidence_score, reverse=True)
    
    def _create_summary(self, themes: List[DetectedTheme]) -> Dict[str, Any]:
        """Create a summary of detected themes."""
        if not themes:
            return {"total": 0, "message": "No universal themes detected"}
        
        total_confidence = sum(t.confidence_score for t in themes)
        avg_confidence = total_confidence / len(themes)
        
        theme_names = [t.theme_name for t in themes]
        most_confident = max(themes, key=lambda t: t.confidence_score)
        
        return {
            "total": len(themes),
            "average_confidence": round(avg_confidence, 2),
            "most_confident_theme": most_confident.theme_name,
            "themes_found": theme_names,
            "message": f"Detected {len(themes)} universal spiritual themes"
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
