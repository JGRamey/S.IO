"""Doctrine analysis agent for identifying and tracking religious doctrines."""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

from solomon.config import settings
from .base import BaseAgent, AgentResult


class DoctrineDefinition(BaseModel):
    """Structure for doctrine definitions."""
    name: str
    description: str
    tradition: str
    denomination: Optional[str] = None
    keywords: List[str]
    related_concepts: List[str]
    historical_context: Optional[str] = None


class DetectedDoctrine(BaseModel):
    """Structure for detected doctrines in text."""
    doctrine_name: str
    tradition: str
    denomination: Optional[str] = None
    confidence_score: float
    text_excerpts: List[str]
    explanation: str
    historical_context: Optional[str] = None
    evolution_notes: Optional[str] = None


class DoctrineAnalysisAgent(BaseAgent):
    """Agent for analyzing and tracking religious doctrines across texts."""
    
    DOCTRINE_DEFINITIONS = {
        # Christian Doctrines
        "trinity": DoctrineDefinition(
            name="Trinity",
            description="The doctrine that God exists as three persons: Father, Son, and Holy Spirit",
            tradition="Christianity",
            keywords=["trinity", "father", "son", "holy spirit", "three persons", "godhead"],
            related_concepts=["incarnation", "divine nature", "hypostasis", "consubstantial"],
            historical_context="Formalized at Council of Nicaea (325 CE) and Constantinople (381 CE)"
        ),
        "incarnation": DoctrineDefinition(
            name="Incarnation",
            description="The belief that Jesus Christ is both fully God and fully human",
            tradition="Christianity",
            keywords=["incarnation", "god-man", "divine nature", "human nature", "hypostatic union"],
            related_concepts=["christology", "two natures", "theotokos", "logos"],
            historical_context="Defined at Council of Chalcedon (451 CE)"
        ),
        "salvation_by_grace": DoctrineDefinition(
            name="Salvation by Grace",
            description="The doctrine that salvation comes through God's grace, not human works",
            tradition="Christianity",
            denomination="Protestant",
            keywords=["grace", "faith alone", "sola gratia", "justification", "salvation"],
            related_concepts=["atonement", "redemption", "sanctification", "predestination"],
            historical_context="Emphasized during Protestant Reformation (16th century)"
        ),
        "transubstantiation": DoctrineDefinition(
            name="Transubstantiation",
            description="The doctrine that bread and wine become the actual body and blood of Christ",
            tradition="Christianity",
            denomination="Catholic",
            keywords=["transubstantiation", "eucharist", "real presence", "substance", "accidents"],
            related_concepts=["mass", "communion", "sacrament", "consecration"],
            historical_context="Formally defined at Fourth Lateran Council (1215 CE)"
        ),
        
        # Islamic Doctrines
        "tawhid": DoctrineDefinition(
            name="Tawhid",
            description="The absolute oneness and unity of Allah",
            tradition="Islam",
            keywords=["tawhid", "oneness", "unity", "allah", "monotheism", "la ilaha illa allah"],
            related_concepts=["shirk", "monotheism", "divine unity", "absolute"],
            historical_context="Central doctrine from the beginning of Islam"
        ),
        "prophethood": DoctrineDefinition(
            name="Prophethood",
            description="The belief in prophets as messengers of Allah, with Muhammad as the final prophet",
            tradition="Islam",
            keywords=["prophet", "messenger", "rasul", "nabi", "muhammad", "final prophet"],
            related_concepts=["revelation", "quran", "sunnah", "seal of prophets"],
            historical_context="Fundamental Islamic belief from the Quran"
        ),
        "predestination_qadar": DoctrineDefinition(
            name="Qadar (Predestination)",
            description="The doctrine of divine predestination and decree",
            tradition="Islam",
            keywords=["qadar", "predestination", "divine decree", "fate", "destiny"],
            related_concepts=["free will", "divine knowledge", "determinism", "taqdir"],
            historical_context="Debated extensively in early Islamic theology"
        ),
        
        # Jewish Doctrines
        "chosen_people": DoctrineDefinition(
            name="Chosen People",
            description="The belief that the Jewish people have a special covenant with God",
            tradition="Judaism",
            keywords=["chosen people", "covenant", "election", "israel", "special relationship"],
            related_concepts=["brit", "torah", "mitzvot", "promised land"],
            historical_context="Rooted in Abrahamic and Mosaic covenants"
        ),
        "torah_divine": DoctrineDefinition(
            name="Divine Torah",
            description="The belief that the Torah is the direct word of God given to Moses",
            tradition="Judaism",
            keywords=["torah", "divine revelation", "moses", "sinai", "word of god"],
            related_concepts=["oral law", "written law", "revelation", "commandments"],
            historical_context="Central to Jewish faith and practice"
        ),
        
        # Hindu Doctrines
        "karma": DoctrineDefinition(
            name="Karma",
            description="The law of cause and effect governing actions and their consequences",
            tradition="Hinduism",
            keywords=["karma", "action", "consequence", "cause and effect", "moral law"],
            related_concepts=["dharma", "samsara", "moksha", "reincarnation"],
            historical_context="Developed in Upanishads and classical Hindu texts"
        ),
        "dharma": DoctrineDefinition(
            name="Dharma",
            description="Righteous duty and moral law governing individual and social conduct",
            tradition="Hinduism",
            keywords=["dharma", "duty", "righteousness", "moral law", "cosmic order"],
            related_concepts=["karma", "varna", "ashrama", "rita"],
            historical_context="Central concept in Hindu ethics and philosophy"
        ),
        "moksha": DoctrineDefinition(
            name="Moksha",
            description="Liberation from the cycle of birth, death, and rebirth",
            tradition="Hinduism",
            keywords=["moksha", "liberation", "release", "salvation", "freedom"],
            related_concepts=["samsara", "nirvana", "enlightenment", "self-realization"],
            historical_context="Ultimate goal in Hindu spiritual practice"
        ),
        
        # Buddhist Doctrines
        "four_noble_truths": DoctrineDefinition(
            name="Four Noble Truths",
            description="The fundamental Buddhist teaching about suffering and its cessation",
            tradition="Buddhism",
            keywords=["four noble truths", "suffering", "dukkha", "cessation", "path"],
            related_concepts=["eightfold path", "nirvana", "enlightenment", "buddha"],
            historical_context="Buddha's first teaching after enlightenment"
        ),
        "no_self": DoctrineDefinition(
            name="Anatman (No-Self)",
            description="The doctrine that there is no permanent, unchanging self or soul",
            tradition="Buddhism",
            keywords=["anatman", "no-self", "anatta", "impermanence", "non-self"],
            related_concepts=["impermanence", "interdependence", "emptiness", "skandhas"],
            historical_context="Distinguishes Buddhism from Hindu concepts of atman"
        ),
    }
    
    def __init__(self):
        super().__init__(
            name="doctrine_analysis",
            description="Analyzes and tracks religious doctrines across spiritual texts"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute doctrine analysis on provided text."""
        try:
            text = input_data.get("text", "")
            text_id = input_data.get("text_id")
            tradition = input_data.get("tradition", "")
            denomination = input_data.get("denomination")
            historical_period = input_data.get("historical_period")
            
            if not text:
                return self._create_result(
                    success=False,
                    error="Text parameter is required"
                )
            
            # Detect doctrines using multiple methods
            detected_doctrines = await self._detect_doctrines(text, tradition, denomination)
            
            # Analyze doctrinal evolution if historical context provided
            evolution_analysis = await self._analyze_doctrinal_evolution(
                detected_doctrines, historical_period
            ) if historical_period else {}
            
            # Score and rank doctrines
            ranked_doctrines = self._rank_doctrines(detected_doctrines)
            
            return self._create_result(
                success=True,
                data={
                    "text_id": text_id,
                    "tradition": tradition,
                    "denomination": denomination,
                    "doctrines_detected": len(ranked_doctrines),
                    "doctrines": [d.dict() for d in ranked_doctrines],
                    "evolution_analysis": evolution_analysis,
                    "analysis_summary": self._create_summary(ranked_doctrines)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Doctrine analysis failed: {e}")
            return self._create_result(
                success=False,
                error=str(e)
            )
    
    async def _detect_doctrines(
        self,
        text: str,
        tradition: str = "",
        denomination: Optional[str] = None
    ) -> List[DetectedDoctrine]:
        """Detect doctrines using multiple detection methods."""
        detected = []
        
        # Method 1: Keyword-based detection
        keyword_doctrines = self._detect_by_keywords(text, tradition, denomination)
        detected.extend(keyword_doctrines)
        
        # Method 2: Contextual pattern detection
        pattern_doctrines = self._detect_by_patterns(text, tradition)
        detected.extend(pattern_doctrines)
        
        # Method 3: LLM-based detection
        llm_doctrines = await self._detect_by_llm(text, tradition, denomination)
        detected.extend(llm_doctrines)
        
        # Merge and deduplicate
        return self._merge_doctrine_detections(detected)
    
    def _detect_by_keywords(
        self,
        text: str,
        tradition: str = "",
        denomination: Optional[str] = None
    ) -> List[DetectedDoctrine]:
        """Detect doctrines using keyword matching."""
        detected = []
        text_lower = text.lower()
        
        # Filter doctrines by tradition if specified
        relevant_doctrines = {}
        for key, doctrine in self.DOCTRINE_DEFINITIONS.items():
            if not tradition or doctrine.tradition.lower() == tradition.lower():
                if not denomination or not doctrine.denomination or doctrine.denomination.lower() == denomination.lower():
                    relevant_doctrines[key] = doctrine
        
        for doctrine_key, doctrine_info in relevant_doctrines.items():
            matched_keywords = []
            matched_excerpts = []
            
            # Check for keywords and related concepts
            all_keywords = doctrine_info.keywords + doctrine_info.related_concepts
            
            for keyword in all_keywords:
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)
                    # Find sentences containing the keyword
                    sentences = self._split_into_sentences(text)
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            matched_excerpts.append(sentence)
            
            if matched_keywords:
                confidence = min(len(matched_keywords) * 0.25, 0.9)
                
                detected.append(DetectedDoctrine(
                    doctrine_name=doctrine_info.name,
                    tradition=doctrine_info.tradition,
                    denomination=doctrine_info.denomination,
                    confidence_score=confidence,
                    text_excerpts=matched_excerpts[:3],
                    explanation=f"Keywords found: {', '.join(matched_keywords)}",
                    historical_context=doctrine_info.historical_context
                ))
        
        return detected
    
    def _detect_by_patterns(self, text: str, tradition: str = "") -> List[DetectedDoctrine]:
        """Detect doctrines using contextual patterns."""
        detected = []
        
        # Pattern for Trinity (Christian)
        trinity_patterns = [
            r"father\s+(?:and\s+)?son\s+(?:and\s+)?holy\s+spirit",
            r"three\s+persons?\s+(?:in\s+)?one\s+god",
            r"godhead\s+(?:of\s+)?three",
        ]
        
        for pattern in trinity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append(DetectedDoctrine(
                    doctrine_name="Trinity",
                    tradition="Christianity",
                    confidence_score=0.7,
                    text_excerpts=[self._get_sentence_containing_position(text, match.start())],
                    explanation="Pattern suggests Trinity doctrine",
                    historical_context=self.DOCTRINE_DEFINITIONS["trinity"].historical_context
                ))
        
        # Pattern for Tawhid (Islamic)
        tawhid_patterns = [
            r"la\s+ilaha\s+illa\s+allah",
            r"oneness\s+of\s+allah",
            r"allah\s+is\s+one",
        ]
        
        for pattern in tawhid_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append(DetectedDoctrine(
                    doctrine_name="Tawhid",
                    tradition="Islam",
                    confidence_score=0.8,
                    text_excerpts=[self._get_sentence_containing_position(text, match.start())],
                    explanation="Pattern suggests Tawhid doctrine",
                    historical_context=self.DOCTRINE_DEFINITIONS["tawhid"].historical_context
                ))
        
        return detected
    
    async def _detect_by_llm(
        self,
        text: str,
        tradition: str = "",
        denomination: Optional[str] = None
    ) -> List[DetectedDoctrine]:
        """Detect doctrines using LLM analysis."""
        try:
            system_prompt = """You are an expert in religious studies and theology. Your task is to identify specific religious doctrines in the provided text.

Focus on identifying these types of doctrines:
- Core theological beliefs (Trinity, Tawhid, etc.)
- Salvation doctrines (Grace, Karma, etc.)
- Eschatological beliefs (Afterlife, Judgment, etc.)
- Sacramental doctrines (Transubstantiation, etc.)
- Ethical teachings (Dharma, Commandments, etc.)

For each doctrine you identify, provide:
- The specific doctrine name
- The religious tradition it belongs to
- Denomination if applicable
- Confidence score (0.0 to 1.0)
- Text excerpts that express this doctrine
- Brief explanation of how the text expresses this doctrine

Respond in JSON format."""
            
            tradition_context = f"This text is from the {tradition} tradition" if tradition else "Analyze for any religious tradition"
            denomination_context = f" ({denomination} denomination)" if denomination else ""
            
            analysis_prompt = f"""Identify specific religious doctrines in this text:

Context: {tradition_context}{denomination_context}

Text to analyze:
{text}

Identify doctrines and respond in this JSON format:
{{
  "doctrines": [
    {{
      "name": "doctrine_name",
      "tradition": "tradition_name",
      "denomination": "denomination_name",
      "excerpts": ["relevant text excerpt 1", "relevant text excerpt 2"],
      "confidence": 0.8,
      "explanation": "how this doctrine is expressed in the text"
    }}
  ]
}}"""
            
            response = await self._analyze_text(text, analysis_prompt, system_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                detected = []
                
                for doctrine_data in result.get("doctrines", []):
                    doctrine_name = doctrine_data.get("name", "")
                    
                    # Map to our standard doctrine names
                    mapped_doctrine = self._map_doctrine_name(doctrine_name)
                    if mapped_doctrine:
                        detected.append(DetectedDoctrine(
                            doctrine_name=mapped_doctrine,
                            tradition=doctrine_data.get("tradition", tradition),
                            denomination=doctrine_data.get("denomination", denomination),
                            confidence_score=doctrine_data.get("confidence", 0.5),
                            text_excerpts=doctrine_data.get("excerpts", []),
                            explanation=doctrine_data.get("explanation", ""),
                            historical_context=self._get_doctrine_historical_context(mapped_doctrine)
                        ))
                
                return detected
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse LLM JSON response")
                return self._parse_llm_text_response(response, tradition)
                
        except Exception as e:
            self.logger.error(f"LLM doctrine detection failed: {e}")
            return []
    
    def _map_doctrine_name(self, llm_doctrine_name: str) -> Optional[str]:
        """Map LLM-generated doctrine name to our standard doctrines."""
        llm_lower = llm_doctrine_name.lower()
        
        # Direct name matching
        for doctrine_key, doctrine_info in self.DOCTRINE_DEFINITIONS.items():
            if (doctrine_info.name.lower() in llm_lower or 
                llm_lower in doctrine_info.name.lower()):
                return doctrine_info.name
        
        # Keyword matching
        for doctrine_key, doctrine_info in self.DOCTRINE_DEFINITIONS.items():
            for keyword in doctrine_info.keywords:
                if keyword.lower() in llm_lower:
                    return doctrine_info.name
        
        return None
    
    def _get_doctrine_historical_context(self, doctrine_name: str) -> Optional[str]:
        """Get historical context for a doctrine."""
        for doctrine_key, doctrine_info in self.DOCTRINE_DEFINITIONS.items():
            if doctrine_info.name == doctrine_name:
                return doctrine_info.historical_context
        return None
    
    def _parse_llm_text_response(self, response: str, tradition: str = "") -> List[DetectedDoctrine]:
        """Parse non-JSON LLM response for doctrines."""
        detected = []
        
        for doctrine_key, doctrine_info in self.DOCTRINE_DEFINITIONS.items():
            if (not tradition or doctrine_info.tradition.lower() == tradition.lower()) and \
               doctrine_info.name.lower() in response.lower():
                
                # Extract context around the doctrine mention
                lines = response.split('\n')
                relevant_lines = []
                
                for line in lines:
                    if doctrine_info.name.lower() in line.lower():
                        relevant_lines.append(line.strip())
                
                if relevant_lines:
                    detected.append(DetectedDoctrine(
                        doctrine_name=doctrine_info.name,
                        tradition=doctrine_info.tradition,
                        denomination=doctrine_info.denomination,
                        confidence_score=0.4,
                        text_excerpts=relevant_lines[:2],
                        explanation=f"LLM identified {doctrine_info.name}",
                        historical_context=doctrine_info.historical_context
                    ))
        
        return detected
    
    async def _analyze_doctrinal_evolution(
        self,
        detected_doctrines: List[DetectedDoctrine],
        historical_period: str
    ) -> Dict[str, Any]:
        """Analyze how doctrines evolved in the given historical period."""
        if not detected_doctrines:
            return {}
        
        try:
            doctrines_list = [d.doctrine_name for d in detected_doctrines]
            
            system_prompt = """You are an expert in the historical development of religious doctrines. 
            Analyze how the specified doctrines evolved during the given historical period."""
            
            analysis_prompt = f"""Analyze the evolution of these doctrines during {historical_period}:

Doctrines: {', '.join(doctrines_list)}

For each doctrine, describe:
1. How it was understood during this period
2. Any changes or developments that occurred
3. Key figures or events that influenced its development
4. Controversies or debates surrounding it

Provide a brief analysis for each doctrine."""
            
            response = await self._analyze_text("", analysis_prompt, system_prompt)
            
            return {
                "historical_period": historical_period,
                "analysis": response,
                "doctrines_analyzed": doctrines_list
            }
            
        except Exception as e:
            self.logger.error(f"Doctrinal evolution analysis failed: {e}")
            return {}
    
    def _merge_doctrine_detections(self, detected: List[DetectedDoctrine]) -> List[DetectedDoctrine]:
        """Merge similar doctrine detections."""
        doctrine_groups = defaultdict(list)
        
        # Group by doctrine name
        for doctrine in detected:
            doctrine_groups[doctrine.doctrine_name].append(doctrine)
        
        merged = []
        for doctrine_name, doctrines in doctrine_groups.items():
            if len(doctrines) == 1:
                merged.append(doctrines[0])
            else:
                # Merge multiple detections of the same doctrine
                best_doctrine = max(doctrines, key=lambda d: d.confidence_score)
                
                # Combine excerpts and explanations
                all_excerpts = []
                all_explanations = []
                
                for doctrine in doctrines:
                    all_excerpts.extend(doctrine.text_excerpts)
                    all_explanations.append(doctrine.explanation)
                
                # Remove duplicates and limit
                unique_excerpts = list(dict.fromkeys(all_excerpts))[:5]
                combined_explanation = "; ".join(set(all_explanations))
                
                merged_doctrine = DetectedDoctrine(
                    doctrine_name=doctrine_name,
                    tradition=best_doctrine.tradition,
                    denomination=best_doctrine.denomination,
                    confidence_score=best_doctrine.confidence_score,
                    text_excerpts=unique_excerpts,
                    explanation=combined_explanation,
                    historical_context=best_doctrine.historical_context
                )
                merged.append(merged_doctrine)
        
        return merged
    
    def _rank_doctrines(self, doctrines: List[DetectedDoctrine]) -> List[DetectedDoctrine]:
        """Rank doctrines by confidence score and importance."""
        return sorted(doctrines, key=lambda d: d.confidence_score, reverse=True)
    
    def _create_summary(self, doctrines: List[DetectedDoctrine]) -> Dict[str, Any]:
        """Create a summary of detected doctrines."""
        if not doctrines:
            return {"total": 0, "message": "No religious doctrines detected"}
        
        tradition_counts = defaultdict(int)
        denomination_counts = defaultdict(int)
        
        for doctrine in doctrines:
            tradition_counts[doctrine.tradition] += 1
            if doctrine.denomination:
                denomination_counts[doctrine.denomination] += 1
        
        total_confidence = sum(d.confidence_score for d in doctrines)
        avg_confidence = total_confidence / len(doctrines)
        
        most_confident = max(doctrines, key=lambda d: d.confidence_score)
        
        return {
            "total": len(doctrines),
            "average_confidence": round(avg_confidence, 2),
            "most_confident_doctrine": most_confident.doctrine_name,
            "traditions": dict(tradition_counts),
            "denominations": dict(denomination_counts),
            "doctrines_found": [d.doctrine_name for d in doctrines],
            "message": f"Detected {len(doctrines)} religious doctrines"
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_sentence_containing_position(self, text: str, position: int) -> str:
        """Get the sentence containing a specific character position."""
        sentences = self._split_into_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            if current_pos <= position <= current_pos + len(sentence):
                return sentence
            current_pos += len(sentence) + 1
        
        return ""
