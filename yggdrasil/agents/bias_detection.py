"""
Bias Detection Agent for identifying various forms of bias in spiritual and philosophical texts.

This agent analyzes content for cognitive biases, cultural biases, confirmation bias,
selection bias, and other forms of systematic deviation from neutrality or objectivity.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        pass

class AgentResult:
    def __init__(self, success: bool, data: Dict[str, Any], metadata: Dict[str, Any], error_message: str = None):
        self.success = success
        self.data = data
        self.metadata = metadata
        self.error_message = error_message

class LLM(ABC):
    @abstractmethod
    async def agenerate(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

class HumanMessage:
    def __init__(self, content: str):
        self.content = content

class SystemMessage:
    def __init__(self, content: str):
        self.content = content

from .base import BaseAgent, AgentResult
from langchain.llms.base import LLM
from langchain.schema import HumanMessage, SystemMessage


@dataclass
class BiasDetection:
    """Represents a detected bias instance."""
    bias_type: str
    confidence: float
    text_snippet: str
    explanation: str
    severity: str  # low, medium, high, critical
    start_position: int
    end_position: int
    suggestions: List[str]
    category: str  # cognitive, cultural, confirmation, selection, etc.


class BiasDetectionAgent(BaseAgent):
    """Agent for detecting various forms of bias in spiritual and philosophical content."""
    
    # Comprehensive bias taxonomy for spiritual/philosophical content
    BIAS_TYPES = {
        # Cognitive Biases
        "confirmation_bias": {
            "description": "Tendency to search for, interpret, and remember information that confirms pre-existing beliefs",
            "category": "cognitive",
            "keywords": ["obviously", "clearly", "any reasonable person", "it's evident that", "undoubtedly"]
        },
        "selection_bias": {
            "description": "Systematic error in selecting sources or examples that support a particular viewpoint",
            "category": "selection",
            "keywords": ["cherry-picking", "only", "exclusively", "ignore", "dismiss without consideration"]
        },
        "authority_bias": {
            "description": "Tendency to attribute greater accuracy to the opinion of an authority figure",
            "category": "cognitive",
            "keywords": ["the church says", "ancient wisdom", "scholars agree", "tradition teaches", "authorities confirm"]
        },
        "in_group_bias": {
            "description": "Tendency to favor one's own group over others",
            "category": "social",
            "keywords": ["we", "us", "our way", "outsiders", "they don't understand", "only we know"]
        },
        "cultural_supremacy": {
            "description": "Belief that one's own culture or tradition is superior to others",
            "category": "cultural",
            "keywords": ["primitive", "advanced", "enlightened vs unenlightened", "higher truth", "superior path"]
        },
        "chronological_snobbery": {
            "description": "Assumption that newer ideas are necessarily better than older ones, or vice versa",
            "category": "temporal",
            "keywords": ["outdated", "modern understanding", "ancient wisdom", "primitive thinking", "evolved beyond"]
        },
        "gender_bias": {
            "description": "Systematic prejudice or discrimination based on gender",
            "category": "social",
            "keywords": ["women are naturally", "men should", "feminine weakness", "masculine strength", "natural role"]
        },
        "survivorship_bias": {
            "description": "Logical error focusing on successful outcomes while ignoring failures",
            "category": "logical",
            "keywords": ["successful practitioners", "those who achieved", "masters who", "ignore failures"]
        },
        "false_dichotomy": {
            "description": "Presenting only two options when more exist",
            "category": "logical",
            "keywords": ["either...or", "only two paths", "must choose", "binary choice", "no middle ground"]
        },
        "hasty_generalization": {
            "description": "Drawing broad conclusions from insufficient evidence",
            "category": "logical",
            "keywords": ["all", "every", "always", "never", "without exception", "universally true"]
        },
        "religious_exclusivism": {
            "description": "Claim that only one religious tradition possesses ultimate truth",
            "category": "religious",
            "keywords": ["only true path", "exclusive truth", "chosen people", "one way", "false religions"]
        },
        "spiritual_materialism": {
            "description": "Using spiritual practices to reinforce ego rather than transcend it",
            "category": "spiritual",
            "keywords": ["spiritual superiority", "more enlightened", "higher level", "spiritual achievement", "evolved souls"]
        }
    }
    
    SEVERITY_INDICATORS = {
        "critical": ["absolutely false", "complete nonsense", "totally wrong", "utterly misguided"],
        "high": ["clearly wrong", "obviously false", "certainly incorrect", "definitely misguided"],
        "medium": ["probably wrong", "likely incorrect", "seems misguided", "appears false"],
        "low": ["might be wrong", "could be incorrect", "questionable", "somewhat biased"]
    }
    
    def __init__(self):
        super().__init__(
            name="bias_detection",
            description="Detects various forms of bias in spiritual and philosophical content"
        )
        self.analysis_cache = {}
        self.llm = None
        
    async def analyze_text(self, text: str, **kwargs) -> AgentResult:
        """
        Analyze text for various forms of bias.
        
        Args:
            text: Text to analyze for bias
            **kwargs: Additional parameters including:
                - domain: Content domain (philosophy, religion, spirituality)
                - tradition: Specific tradition (optional)
                - context: Additional context for analysis
                - sensitivity: Analysis sensitivity (low, medium, high)
        
        Returns:
            AgentResult with detected biases and recommendations
        """
        try:
            domain = kwargs.get('domain', 'spirituality')
            tradition = kwargs.get('tradition', 'universal')
            sensitivity = kwargs.get('sensitivity', 'medium')
            context = kwargs.get('context', '')
            
            # Multi-layered bias analysis
            pattern_biases = await self._detect_pattern_biases(text, sensitivity)
            linguistic_biases = await self._detect_linguistic_biases(text)
            logical_biases = await self._detect_logical_biases(text)
            cultural_biases = await self._detect_cultural_biases(text, tradition)
            ai_detected_biases = await self._ai_bias_analysis(text, domain, context)
            
            # Combine all detected biases
            all_biases = pattern_biases + linguistic_biases + logical_biases + cultural_biases + ai_detected_biases
            
            # Remove duplicates and rank by confidence
            unique_biases = self._deduplicate_biases(all_biases)
            ranked_biases = sorted(unique_biases, key=lambda x: x.confidence, reverse=True)
            
            # Generate overall bias assessment
            bias_summary = self._generate_bias_summary(ranked_biases, text)
            
            # Create recommendations
            recommendations = self._generate_recommendations(ranked_biases, domain)
            
            result_data = {
                "detected_biases": [self._bias_to_dict(bias) for bias in ranked_biases],
                "bias_summary": bias_summary,
                "recommendations": recommendations,
                "overall_bias_score": self._calculate_overall_bias_score(ranked_biases),
                "analysis_metadata": {
                    "domain": domain,
                    "tradition": tradition,
                    "sensitivity": sensitivity,
                    "total_biases_found": len(ranked_biases),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                metadata={
                    "agent_name": self.name,
                    "analysis_type": "bias_detection",
                    "processing_time": 0.0  # Will be set by base class
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error_message=f"Bias detection failed: {str(e)}",
                data={"biases": [], "error_details": str(e)}
            )
    
    async def _detect_pattern_biases(self, text: str, sensitivity: str) -> List[BiasDetection]:
        """Detect biases using pattern matching."""
        biases = []
        
        # Adjust sensitivity
        confidence_threshold = {"low": 0.3, "medium": 0.5, "high": 0.7}.get(sensitivity, 0.5)
        
        for bias_type, info in self.BIAS_TYPES.items():
            for keyword in info["keywords"]:
                pattern = rf'\b{re.escape(keyword)}\b'
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    # Calculate confidence based on context
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(text), match.end() + 50)
                    context = text[context_start:context_end]
                    
                    confidence = self._calculate_pattern_confidence(keyword, context, bias_type)
                    
                    if confidence >= confidence_threshold:
                        severity = self._determine_severity(context)
                        suggestions = self._generate_bias_suggestions(bias_type, keyword)
                        
                        bias = BiasDetection(
                            bias_type=bias_type,
                            confidence=confidence,
                            text_snippet=match.group(),
                            explanation=info["description"],
                            severity=severity,
                            start_position=match.start(),
                            end_position=match.end(),
                            suggestions=suggestions,
                            category=info["category"]
                        )
                        biases.append(bias)
        
        return biases
    
    async def _detect_linguistic_biases(self, text: str) -> List[BiasDetection]:
        """Detect biases through linguistic analysis."""
        biases = []
        
        # Absolute language detection
        absolute_patterns = [
            r'\b(always|never|all|none|every|no one|everyone|everything|nothing)\b',
            r'\b(completely|totally|absolutely|entirely|perfectly)\b',
            r'\b(must|should|ought to|have to|need to)\s+(?:be|do|believe|accept)'
        ]
        
        for pattern in absolute_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 30)
                context_end = min(len(text), match.end() + 30)
                context = text[context_start:context_end]
                
                bias = BiasDetection(
                    bias_type="absolute_thinking",
                    confidence=0.6,
                    text_snippet=match.group(),
                    explanation="Use of absolute language that doesn't allow for exceptions or nuance",
                    severity="medium",
                    start_position=match.start(),
                    end_position=match.end(),
                    suggestions=["Consider using more nuanced language", "Allow for exceptions", "Use qualifiers like 'often' or 'generally'"],
                    category="linguistic"
                )
                biases.append(bias)
        
        return biases
    
    async def _detect_logical_biases(self, text: str) -> List[BiasDetection]:
        """Detect logical fallacies and reasoning biases."""
        biases = []
        
        # Straw man indicators
        straw_man_patterns = [
            r'critics claim that we believe',
            r'opponents say that',
            r'they think we',
            r'misrepresent our position',
        ]
        
        # Ad hominem indicators  
        ad_hominem_patterns = [
            r'those who disagree are',
            r'critics are just',
            r'opponents are merely',
            r'anyone who believes otherwise is',
        ]
        
        # Appeal to tradition
        tradition_patterns = [
            r'this has always been',
            r'traditional wisdom',
            r'ancient knowledge',
            r'time-tested truth',
        ]
        
        logical_patterns = {
            "straw_man": straw_man_patterns,
            "ad_hominem": ad_hominem_patterns,
            "appeal_to_tradition": tradition_patterns
        }
        
        for bias_type, patterns in logical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    bias = BiasDetection(
                        bias_type=bias_type,
                        confidence=0.7,
                        text_snippet=match.group(),
                        explanation=f"Potential {bias_type.replace('_', ' ')} logical fallacy",
                        severity="medium",
                        start_position=match.start(),
                        end_position=match.end(),
                        suggestions=[f"Avoid {bias_type.replace('_', ' ')}", "Present opponents' views fairly", "Use logical reasoning"],
                        category="logical"
                    )
                    biases.append(bias)
        
        return biases
    
    async def _detect_cultural_biases(self, text: str, tradition: str) -> List[BiasDetection]:
        """Detect cultural and religious biases."""
        biases = []
        
        # Western-centric language
        western_bias_patterns = [
            r'primitive beliefs',
            r'advanced civilization',
            r'developed nations',
            r'third world thinking',
            r'modern enlightenment'
        ]
        
        # Religious supremacy patterns
        supremacy_patterns = [
            r'one true',
            r'only path',
            r'chosen people',
            r'false religion',
            r'heretical belief'
        ]
        
        cultural_patterns = {
            "western_centrism": western_bias_patterns,
            "religious_supremacy": supremacy_patterns
        }
        
        for bias_type, patterns in cultural_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    bias = BiasDetection(
                        bias_type=bias_type,
                        confidence=0.8,
                        text_snippet=match.group(),
                        explanation=f"Potential {bias_type.replace('_', ' ')} bias",
                        severity="high",
                        start_position=match.start(),
                        end_position=match.end(),
                        suggestions=["Use culturally neutral language", "Respect diverse perspectives", "Avoid supremacist language"],
                        category="cultural"
                    )
                    biases.append(bias)
        
        return biases
    
    async def _ai_bias_analysis(self, text: str, domain: str, context: str) -> List[BiasDetection]:
        """Use AI to detect subtle biases that pattern matching might miss."""
        if not self.llm:
            return []
        
        try:
            prompt = f"""
            Analyze the following {domain} text for subtle biases, prejudices, or unfair assumptions.
            
            Text: "{text}"
            Context: {context}
            
            Look for:
            1. Implicit assumptions about gender, culture, or social class
            2. Subtle confirmation bias or cherry-picking
            3. Unstated premises that favor one viewpoint
            4. Language that dismisses alternative perspectives
            5. Cultural or religious chauvinism
            
            For each bias detected, provide:
            - Type of bias
            - Confidence score (0.0-1.0)
            - Specific text snippet
            - Brief explanation
            - Severity (low/medium/high)
            
            Respond in JSON format with an array of bias objects.
            """
            
            messages = [
                SystemMessage(content="You are an expert in detecting bias in philosophical and spiritual texts."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            result_text = response.generations[0][0].text.strip()
            
            # Parse JSON response
            try:
                bias_data = json.loads(result_text)
                biases = []
                
                for item in bias_data:
                    if isinstance(item, dict) and all(k in item for k in ['type', 'confidence', 'snippet']):
                        bias = BiasDetection(
                            bias_type=item.get('type', 'unknown'),
                            confidence=float(item.get('confidence', 0.5)),
                            text_snippet=item.get('snippet', ''),
                            explanation=item.get('explanation', 'AI-detected bias'),
                            severity=item.get('severity', 'medium'),
                            start_position=text.find(item.get('snippet', '')),
                            end_position=text.find(item.get('snippet', '')) + len(item.get('snippet', '')),
                            suggestions=item.get('suggestions', ['Consider alternative perspectives']),
                            category="ai_detected"
                        )
                        biases.append(bias)
                
                return biases
                
            except json.JSONDecodeError:
                return []
            
        except Exception as e:
            return []
    
    def _calculate_pattern_confidence(self, keyword: str, context: str, bias_type: str) -> float:
        """Calculate confidence score for pattern-based detection."""
        base_confidence = 0.5
        
        # Increase confidence if context supports the bias
        supporting_words = {
            "confirmation_bias": ["proven", "fact", "truth", "obvious"],
            "authority_bias": ["expert", "master", "teacher", "leader"],
            "in_group_bias": ["we", "us", "our", "they", "them"],
            "cultural_supremacy": ["superior", "advanced", "primitive", "backward"]
        }
        
        if bias_type in supporting_words:
            for word in supporting_words[bias_type]:
                if word.lower() in context.lower():
                    base_confidence += 0.1
        
        # Decrease confidence if context has qualifying language
        qualifiers = ["might", "could", "perhaps", "sometimes", "often", "generally"]
        for qualifier in qualifiers:
            if qualifier.lower() in context.lower():
                base_confidence -= 0.1
        
        return max(0.1, min(1.0, base_confidence))
    
    def _determine_severity(self, context: str) -> str:
        """Determine severity based on context."""
        context_lower = context.lower()
        
        for severity, indicators in self.SEVERITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in context_lower:
                    return severity
        
        return "low"
    
    def _generate_bias_suggestions(self, bias_type: str, keyword: str) -> List[str]:
        """Generate suggestions for addressing detected bias."""
        suggestions_map = {
            "confirmation_bias": [
                "Consider counter-arguments",
                "Seek disconfirming evidence",
                "Use more tentative language"
            ],
            "selection_bias": [
                "Include diverse perspectives",
                "Acknowledge limitations",
                "Present opposing views fairly"
            ],
            "authority_bias": [
                "Evaluate arguments on merit",
                "Question authorities",
                "Consider multiple sources"
            ],
            "cultural_supremacy": [
                "Use culturally neutral language",
                "Acknowledge cultural diversity",
                "Avoid value judgments about cultures"
            ],
            "gender_bias": [
                "Use inclusive language",
                "Avoid gender stereotypes",
                "Consider diverse gender perspectives"
            ],
            "religious_exclusivism": [
                "Acknowledge religious diversity",
                "Use respectful language",
                "Avoid absolute truth claims"
            ]
        }
        
        return suggestions_map.get(bias_type, ["Consider alternative perspectives", "Use more neutral language"])
    
    def _deduplicate_biases(self, biases: List[BiasDetection]) -> List[BiasDetection]:
        """Remove duplicate bias detections."""
        seen = set()
        unique_biases = []
        
        for bias in biases:
            # Create a signature for the bias
            signature = (bias.bias_type, bias.start_position, bias.end_position)
            
            if signature not in seen:
                seen.add(signature)
                unique_biases.append(bias)
        
        return unique_biases
    
    def _generate_bias_summary(self, biases: List[BiasDetection], text: str) -> Dict[str, Any]:
        """Generate overall bias summary."""
        if not biases:
            return {
                "overall_assessment": "No significant biases detected",
                "bias_categories": {},
                "total_biases": 0,
                "average_confidence": 0.0,
                "text_bias_density": 0.0
            }
        
        # Categorize biases
        categories = {}
        total_confidence = 0
        
        for bias in biases:
            if bias.category not in categories:
                categories[bias.category] = []
            categories[bias.category].append(bias.bias_type)
            total_confidence += bias.confidence
        
        # Calculate metrics
        avg_confidence = total_confidence / len(biases)
        bias_density = len(biases) / max(1, len(text.split()))
        
        # Overall assessment
        if avg_confidence > 0.8 and len(biases) > 5:
            assessment = "High level of bias detected - significant concerns"
        elif avg_confidence > 0.6 and len(biases) > 3:
            assessment = "Moderate bias detected - some concerns"
        elif len(biases) > 0:
            assessment = "Minor bias detected - generally acceptable"
        else:
            assessment = "No significant bias detected"
        
        return {
            "overall_assessment": assessment,
            "bias_categories": {cat: list(set(types)) for cat, types in categories.items()},
            "total_biases": len(biases),
            "average_confidence": avg_confidence,
            "text_bias_density": bias_density
        }
    
    def _generate_recommendations(self, biases: List[BiasDetection], domain: str) -> List[str]:
        """Generate overall recommendations for reducing bias."""
        if not biases:
            return ["Content appears to be relatively free of bias"]
        
        recommendations = []
        
        # Category-specific recommendations
        categories_present = set(bias.category for bias in biases)
        
        if "cognitive" in categories_present:
            recommendations.append("Review arguments for logical consistency and avoid cognitive shortcuts")
        
        if "cultural" in categories_present:
            recommendations.append("Ensure cultural sensitivity and avoid ethnocentric assumptions")
        
        if "social" in categories_present:
            recommendations.append("Consider diverse social perspectives and avoid in-group favoritism")
        
        if "religious" in categories_present:
            recommendations.append("Respect religious diversity and avoid exclusivist claims")
        
        if "logical" in categories_present:
            recommendations.append("Strengthen logical reasoning and avoid common fallacies")
        
        # General recommendations
        recommendations.extend([
            "Consider having the content reviewed by someone from a different background",
            "Actively seek out opposing viewpoints and address them fairly",
            "Use more tentative language when making broad claims",
            "Provide evidence for assertions rather than assuming agreement"
        ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_overall_bias_score(self, biases: List[BiasDetection]) -> float:
        """Calculate overall bias score (0.0 = no bias, 1.0 = highly biased)."""
        if not biases:
            return 0.0
        
        # Weight by confidence and severity
        severity_weights = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
        
        total_weighted_score = 0
        total_weight = 0
        
        for bias in biases:
            weight = severity_weights.get(bias.severity, 0.5)
            weighted_score = bias.confidence * weight
            total_weighted_score += weighted_score
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(1.0, total_weighted_score / len(biases))
    
    def _bias_to_dict(self, bias: BiasDetection) -> Dict[str, Any]:
        """Convert BiasDetection to dictionary for JSON serialization."""
        return {
            "bias_type": bias.bias_type,
            "confidence": bias.confidence,
            "text_snippet": bias.text_snippet,
            "explanation": bias.explanation,
            "severity": bias.severity,
            "start_position": bias.start_position,
            "end_position": bias.end_position,
            "suggestions": bias.suggestions,
            "category": bias.category
        }
