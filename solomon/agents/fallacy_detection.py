"""Fallacy detection agent for identifying logical fallacies in spiritual texts."""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

from solomon.config import settings
from .base import BaseAgent, AgentResult


class FallacyType(BaseModel):
    """Structure for fallacy types."""
    name: str
    description: str
    examples: List[str]
    keywords: List[str]


class DetectedFallacy(BaseModel):
    """Structure for detected fallacies."""
    fallacy_type: str
    description: str
    context: str
    confidence_score: float
    text_excerpt: str
    explanation: str


class FallacyDetectionAgent(BaseAgent):
    """Agent for detecting logical fallacies in spiritual and religious texts."""
    
    FALLACY_TYPES = {
        "ad_hominem": FallacyType(
            name="Ad Hominem",
            description="Attacking the person making an argument rather than the argument itself",
            examples=[
                "Those who believe differently are fools",
                "Only the ignorant would follow such teachings"
            ],
            keywords=["fool", "ignorant", "stupid", "wicked", "evil person"]
        ),
        "strawman": FallacyType(
            name="Straw Man",
            description="Misrepresenting someone's argument to make it easier to attack",
            examples=[
                "They claim God doesn't exist (when they actually claim lack of evidence)",
                "They want to destroy all tradition (when they want reform)"
            ],
            keywords=["they claim", "they want to", "they believe"]
        ),
        "false_dichotomy": FallacyType(
            name="False Dichotomy",
            description="Presenting only two options when more exist",
            examples=[
                "Either you believe completely or you are against God",
                "You must choose between faith and reason"
            ],
            keywords=["either", "only two", "must choose", "no middle ground"]
        ),
        "appeal_to_authority": FallacyType(
            name="Appeal to Authority",
            description="Claiming something is true because an authority said it, without other evidence",
            examples=[
                "It must be true because the prophet said it",
                "The church fathers declared it, so it's correct"
            ],
            keywords=["because", "declared", "authority", "expert says"]
        ),
        "circular_reasoning": FallacyType(
            name="Circular Reasoning",
            description="Using the conclusion as evidence for the premise",
            examples=[
                "The text is true because it says it's true",
                "God exists because the holy book says so, and the book is true because God wrote it"
            ],
            keywords=["because it says", "proves itself", "self-evident"]
        ),
        "appeal_to_tradition": FallacyType(
            name="Appeal to Tradition",
            description="Claiming something is true or good because it's traditional",
            examples=[
                "We've always done it this way",
                "Our ancestors believed it, so it must be right"
            ],
            keywords=["always done", "tradition", "ancestors", "ancient wisdom"]
        ),
        "slippery_slope": FallacyType(
            name="Slippery Slope",
            description="Claiming that one event will lead to extreme consequences without evidence",
            examples=[
                "If we allow questioning, all faith will be destroyed",
                "Any change will lead to complete moral collapse"
            ],
            keywords=["will lead to", "inevitable", "slippery slope", "domino effect"]
        ),
        "appeal_to_fear": FallacyType(
            name="Appeal to Fear",
            description="Using fear rather than logic to persuade",
            examples=[
                "If you don't believe, you'll be punished eternally",
                "Questioning will bring divine wrath"
            ],
            keywords=["punishment", "wrath", "consequences", "fear", "terrible fate"]
        ),
        "hasty_generalization": FallacyType(
            name="Hasty Generalization",
            description="Drawing broad conclusions from limited examples",
            examples=[
                "All non-believers are immoral",
                "Every member of that faith is extremist"
            ],
            keywords=["all", "every", "always", "never", "everyone"]
        ),
        "no_true_scotsman": FallacyType(
            name="No True Scotsman",
            description="Dismissing counterexamples by redefining terms",
            examples=[
                "No true believer would do that",
                "Real followers wouldn't question"
            ],
            keywords=["no true", "real", "genuine", "authentic"]
        )
    }
    
    def __init__(self):
        super().__init__(
            name="fallacy_detection",
            description="Detects logical fallacies in spiritual and religious texts"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute fallacy detection on provided text."""
        try:
            text = input_data.get("text", "")
            text_id = input_data.get("text_id")
            context = input_data.get("context", "")
            
            if not text:
                return self._create_result(
                    success=False,
                    error="Text parameter is required"
                )
            
            # Detect fallacies using multiple methods
            detected_fallacies = await self._detect_fallacies(text, context)
            
            # Score and rank fallacies
            ranked_fallacies = self._rank_fallacies(detected_fallacies)
            
            return self._create_result(
                success=True,
                data={
                    "text_id": text_id,
                    "fallacies_detected": len(ranked_fallacies),
                    "fallacies": [f.dict() for f in ranked_fallacies],
                    "analysis_summary": self._create_summary(ranked_fallacies)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Fallacy detection failed: {e}")
            return self._create_result(
                success=False,
                error=str(e)
            )
    
    async def _detect_fallacies(self, text: str, context: str = "") -> List[DetectedFallacy]:
        """Detect fallacies using multiple detection methods."""
        detected = []
        
        # Method 1: Keyword-based detection
        keyword_fallacies = self._detect_by_keywords(text)
        detected.extend(keyword_fallacies)
        
        # Method 2: Pattern-based detection
        pattern_fallacies = self._detect_by_patterns(text)
        detected.extend(pattern_fallacies)
        
        # Method 3: LLM-based detection
        llm_fallacies = await self._detect_by_llm(text, context)
        detected.extend(llm_fallacies)
        
        # Remove duplicates and merge similar detections
        return self._merge_duplicate_detections(detected)
    
    def _detect_by_keywords(self, text: str) -> List[DetectedFallacy]:
        """Detect fallacies using keyword matching."""
        detected = []
        text_lower = text.lower()
        
        for fallacy_type, fallacy_info in self.FALLACY_TYPES.items():
            for keyword in fallacy_info.keywords:
                if keyword.lower() in text_lower:
                    # Find the sentence containing the keyword
                    sentences = self._split_into_sentences(text)
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            detected.append(DetectedFallacy(
                                fallacy_type=fallacy_type,
                                description=fallacy_info.description,
                                context=sentence,
                                confidence_score=0.3,  # Low confidence for keyword matching
                                text_excerpt=sentence,
                                explanation=f"Keyword '{keyword}' suggests possible {fallacy_info.name}"
                            ))
                            break
        
        return detected
    
    def _detect_by_patterns(self, text: str) -> List[DetectedFallacy]:
        """Detect fallacies using regex patterns."""
        detected = []
        
        # Pattern for false dichotomy
        false_dichotomy_patterns = [
            r"either\s+.+\s+or\s+.+",
            r"only\s+two\s+.+",
            r"must\s+choose\s+between\s+.+\s+and\s+.+",
        ]
        
        for pattern in false_dichotomy_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append(DetectedFallacy(
                    fallacy_type="false_dichotomy",
                    description=self.FALLACY_TYPES["false_dichotomy"].description,
                    context=self._get_sentence_containing_position(text, match.start()),
                    confidence_score=0.5,
                    text_excerpt=match.group(),
                    explanation="Pattern suggests false dichotomy"
                ))
        
        # Pattern for circular reasoning
        circular_patterns = [
            r"because\s+it\s+says\s+so",
            r"proves\s+itself",
            r"self-evident",
        ]
        
        for pattern in circular_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append(DetectedFallacy(
                    fallacy_type="circular_reasoning",
                    description=self.FALLACY_TYPES["circular_reasoning"].description,
                    context=self._get_sentence_containing_position(text, match.start()),
                    confidence_score=0.6,
                    text_excerpt=match.group(),
                    explanation="Pattern suggests circular reasoning"
                ))
        
        return detected
    
    async def _detect_by_llm(self, text: str, context: str = "") -> List[DetectedFallacy]:
        """Detect fallacies using LLM analysis."""
        try:
            system_prompt = """You are an expert in logic and critical thinking, specializing in identifying logical fallacies in religious and spiritual texts. 

Your task is to analyze the provided text and identify any logical fallacies present. For each fallacy you detect, provide:
1. The type of fallacy
2. The specific text excerpt containing the fallacy
3. An explanation of why it's a fallacy
4. A confidence score (0.0 to 1.0)

Focus on these common fallacies in religious discourse:
- Ad Hominem: Attacking the person rather than the argument
- Straw Man: Misrepresenting an opponent's position
- False Dichotomy: Presenting only two options when more exist
- Appeal to Authority: Claiming truth based solely on authority
- Circular Reasoning: Using the conclusion to prove the premise
- Appeal to Tradition: Claiming truth because it's traditional
- Appeal to Fear: Using fear rather than logic
- Hasty Generalization: Broad conclusions from limited examples
- No True Scotsman: Dismissing counterexamples by redefining terms

Respond in JSON format with an array of detected fallacies."""
            
            analysis_prompt = f"""Analyze this text for logical fallacies:

Context: {context}

Text to analyze:
{text}

Identify any logical fallacies and respond in this JSON format:
{{
  "fallacies": [
    {{
      "type": "fallacy_type",
      "excerpt": "specific text containing the fallacy",
      "explanation": "why this is a fallacy",
      "confidence": 0.8
    }}
  ]
}}"""
            
            response = await self._analyze_text(text, analysis_prompt, system_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                detected = []
                
                for fallacy in result.get("fallacies", []):
                    fallacy_type = fallacy.get("type", "unknown")
                    if fallacy_type in self.FALLACY_TYPES:
                        detected.append(DetectedFallacy(
                            fallacy_type=fallacy_type,
                            description=self.FALLACY_TYPES[fallacy_type].description,
                            context=fallacy.get("excerpt", ""),
                            confidence_score=fallacy.get("confidence", 0.5),
                            text_excerpt=fallacy.get("excerpt", ""),
                            explanation=fallacy.get("explanation", "")
                        ))
                
                return detected
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse LLM JSON response, attempting text parsing")
                return self._parse_llm_text_response(response)
                
        except Exception as e:
            self.logger.error(f"LLM fallacy detection failed: {e}")
            return []
    
    def _parse_llm_text_response(self, response: str) -> List[DetectedFallacy]:
        """Parse non-JSON LLM response for fallacies."""
        detected = []
        
        # Look for fallacy mentions in the response
        for fallacy_type, fallacy_info in self.FALLACY_TYPES.items():
            if fallacy_info.name.lower() in response.lower():
                # Extract relevant context around the fallacy mention
                lines = response.split('\n')
                for line in lines:
                    if fallacy_info.name.lower() in line.lower():
                        detected.append(DetectedFallacy(
                            fallacy_type=fallacy_type,
                            description=fallacy_info.description,
                            context=line,
                            confidence_score=0.4,
                            text_excerpt=line,
                            explanation=f"LLM identified {fallacy_info.name}"
                        ))
                        break
        
        return detected
    
    def _merge_duplicate_detections(self, detected: List[DetectedFallacy]) -> List[DetectedFallacy]:
        """Merge similar fallacy detections."""
        merged = []
        
        for fallacy in detected:
            # Check if we already have a similar detection
            similar_found = False
            for existing in merged:
                if (existing.fallacy_type == fallacy.fallacy_type and 
                    self._text_similarity(existing.text_excerpt, fallacy.text_excerpt) > 0.7):
                    # Merge by taking the higher confidence score
                    if fallacy.confidence_score > existing.confidence_score:
                        existing.confidence_score = fallacy.confidence_score
                        existing.explanation = fallacy.explanation
                    similar_found = True
                    break
            
            if not similar_found:
                merged.append(fallacy)
        
        return merged
    
    def _rank_fallacies(self, fallacies: List[DetectedFallacy]) -> List[DetectedFallacy]:
        """Rank fallacies by confidence score and severity."""
        # Sort by confidence score (descending)
        return sorted(fallacies, key=lambda f: f.confidence_score, reverse=True)
    
    def _create_summary(self, fallacies: List[DetectedFallacy]) -> Dict[str, Any]:
        """Create a summary of detected fallacies."""
        if not fallacies:
            return {"total": 0, "message": "No logical fallacies detected"}
        
        fallacy_counts = {}
        total_confidence = 0
        
        for fallacy in fallacies:
            fallacy_counts[fallacy.fallacy_type] = fallacy_counts.get(fallacy.fallacy_type, 0) + 1
            total_confidence += fallacy.confidence_score
        
        avg_confidence = total_confidence / len(fallacies)
        most_common = max(fallacy_counts.items(), key=lambda x: x[1])
        
        return {
            "total": len(fallacies),
            "average_confidence": round(avg_confidence, 2),
            "most_common_fallacy": most_common[0],
            "fallacy_types": fallacy_counts,
            "message": f"Detected {len(fallacies)} potential logical fallacies"
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (could be improved with NLTK)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_sentence_containing_position(self, text: str, position: int) -> str:
        """Get the sentence containing a specific character position."""
        sentences = self._split_into_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            if current_pos <= position <= current_pos + len(sentence):
                return sentence
            current_pos += len(sentence) + 1  # +1 for the delimiter
        
        return ""
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
