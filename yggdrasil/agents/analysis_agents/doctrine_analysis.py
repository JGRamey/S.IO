"""Enhanced doctrine analysis agent for identifying and tracking religious doctrines with RAG integration."""

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
    """Enhanced agent for analyzing and tracking religious doctrines across texts with RAG integration."""
    
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
            description="The doctrine that Jesus Christ is both fully God and fully human",
            tradition="Christianity",
            keywords=["incarnation", "god-man", "divine nature", "human nature", "hypostatic union"],
            related_concepts=["trinity", "christology", "dual nature"],
            historical_context="Defined at Council of Chalcedon (451 CE)"
        ),
        
        "salvation_by_grace": DoctrineDefinition(
            name="Salvation by Grace",
            description="The doctrine that salvation is by grace through faith, not by works",
            tradition="Christianity",
            denomination="Protestant",
            keywords=["grace", "faith", "salvation", "sola gratia", "justification"],
            related_concepts=["atonement", "redemption", "sanctification"],
            historical_context="Emphasized during Protestant Reformation (16th century)"
        ),
        
        # Islamic Doctrines
        "tawhid": DoctrineDefinition(
            name="Tawhid",
            description="The doctrine of the absolute unity and uniqueness of Allah",
            tradition="Islam",
            keywords=["tawhid", "unity", "oneness", "allah", "monotheism"],
            related_concepts=["shirk", "iman", "islamic monotheism"],
            historical_context="Fundamental principle from Quranic revelation"
        ),
        
        "prophethood": DoctrineDefinition(
            name="Prophethood",
            description="The doctrine regarding prophets as messengers of Allah",
            tradition="Islam",
            keywords=["prophet", "messenger", "nabi", "rasul", "muhammad"],
            related_concepts=["revelation", "quran", "sunnah"],
            historical_context="Central to Islamic belief system"
        ),
        
        # Jewish Doctrines
        "chosen_people": DoctrineDefinition(
            name="Chosen People",
            description="The doctrine that Jews are chosen by God for a special covenant",
            tradition="Judaism",
            keywords=["chosen", "covenant", "israel", "election", "promised land"],
            related_concepts=["torah", "mitzvot", "diaspora"],
            historical_context="Biblical covenant with Abraham and Moses"
        ),
        
        # Buddhist Doctrines
        "four_noble_truths": DoctrineDefinition(
            name="Four Noble Truths",
            description="The fundamental Buddhist teaching about suffering and liberation",
            tradition="Buddhism",
            keywords=["four noble truths", "dukkha", "suffering", "nirvana", "eightfold path"],
            related_concepts=["karma", "rebirth", "enlightenment"],
            historical_context="First sermon of Buddha at Sarnath"
        ),
        
        # Hindu Doctrines
        "karma": DoctrineDefinition(
            name="Karma",
            description="The doctrine of action and consequence across lifetimes",
            tradition="Hinduism",
            keywords=["karma", "action", "consequence", "rebirth", "dharma"],
            related_concepts=["samsara", "moksha", "dharma"],
            historical_context="Ancient Vedic and Upanishadic teaching"
        ),
    }
    
    def __init__(self):
        super().__init__(
            name="DoctrineAnalysisAgent",
            description="Analyzes and tracks religious doctrines across spiritual texts with RAG capabilities",
            enable_rag=True
        )
        
        # Build keyword index for efficient matching
        self.keyword_index = self._build_keyword_index()
        
        # System prompt for doctrine analysis
        self.system_prompt = """You are an expert in comparative religious studies and doctrinal analysis. 
        Your task is to identify, analyze, and explain religious doctrines found in spiritual texts.
        
        When analyzing text for doctrines:
        1. Identify specific doctrines mentioned or implied
        2. Determine the religious tradition and denomination if applicable
        3. Provide confidence scores based on textual evidence
        4. Explain the historical and theological context
        5. Note any doctrinal evolution or variations
        6. Compare with similar doctrines in other traditions
        
        Be scholarly, objective, and respectful of all religious traditions."""
    
    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """Build keyword index for efficient doctrine matching."""
        index = defaultdict(list)
        
        for doctrine_key, definition in self.DOCTRINE_DEFINITIONS.items():
            for keyword in definition.keywords:
                index[keyword.lower()].append(doctrine_key)
                
        return dict(index)
    
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Process a doctrine analysis query with RAG enhancement."""
        try:
            start_time = datetime.now()
            
            # Extract text from context or use query as text
            text = context.get('text', query) if context else query
            text_type = context.get('text_type') if context else None
            
            # Get relevant context using RAG if enabled
            context_texts = []
            if self.enable_rag and context and context.get('enable_rag', True):
                context_texts = await self.get_context_texts(
                    query=f"doctrine analysis: {query}",
                    text_types=[text_type] if text_type else None,
                    limit=3
                )
            
            # Perform doctrine analysis
            doctrine_analysis = await self._analyze_doctrines(text, context_texts)
            
            # Generate enhanced analysis with RAG if context available
            if context_texts and doctrine_analysis['doctrines']:
                enhanced_analysis = await self._enhance_with_rag(
                    text, doctrine_analysis, context_texts
                )
                doctrine_analysis.update(enhanced_analysis)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=doctrine_analysis,
                metadata={
                    'agent_type': 'doctrine_analysis',
                    'text_length': len(text),
                    'rag_context_used': len(context_texts),
                    'doctrines_detected': len(doctrine_analysis.get('doctrines', []))
                },
                execution_time=execution_time,
                sources=[
                    {
                        'title': ctx['title'],
                        'source': ctx.get('source_url', ''),
                        'text_type': ctx['text_type'],
                        'similarity_score': ctx.get('similarity_score', 0.0)
                    }
                    for ctx in context_texts
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Doctrine analysis failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={}
            )
    
    async def _analyze_doctrines(self, text: str, context_texts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze text for religious doctrines."""
        # Initial keyword-based detection
        potential_doctrines = self._detect_potential_doctrines(text)
        
        # Enhanced analysis with LLM
        detected_doctrines = []
        for doctrine_key in potential_doctrines:
            doctrine_analysis = await self._analyze_specific_doctrine(text, doctrine_key, context_texts)
            if doctrine_analysis:
                detected_doctrines.append(doctrine_analysis)
        
        # Cross-tradition analysis
        cross_tradition_analysis = self._analyze_cross_traditions(detected_doctrines)
        
        # Generate summary
        analysis_summary = self._generate_analysis_summary(detected_doctrines)
        
        return {
            'doctrines': detected_doctrines,
            'cross_tradition_analysis': cross_tradition_analysis,
            'analysis_summary': analysis_summary,
            'total_doctrines_detected': len(detected_doctrines)
        }
    
    def _detect_potential_doctrines(self, text: str) -> List[str]:
        """Detect potential doctrines based on keyword matching."""
        text_lower = text.lower()
        potential_doctrines = set()
        
        for keyword, doctrine_keys in self.keyword_index.items():
            if keyword in text_lower:
                potential_doctrines.update(doctrine_keys)
        
        return list(potential_doctrines)
    
    async def _analyze_specific_doctrine(
        self, 
        text: str, 
        doctrine_key: str, 
        context_texts: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze specific doctrine in text with LLM enhancement."""
        definition = self.DOCTRINE_DEFINITIONS[doctrine_key]
        
        # Prepare context information
        context_info = ""
        if context_texts:
            context_info = "\n\nRelevant context from similar texts:\n" + "\n".join([
                f"- {ctx['title']}: {ctx['content'][:200]}..."
                for ctx in context_texts[:2]
            ])
        
        prompt = f"""Analyze the following text for the doctrine of "{definition.name}":

Doctrine Definition:
- Name: {definition.name}
- Description: {definition.description}
- Tradition: {definition.tradition}
- Keywords: {', '.join(definition.keywords)}
- Historical Context: {definition.historical_context}

Text to analyze:
{text[:2000]}...

{context_info}

Please provide:
1. Confidence score (0.0-1.0) that this doctrine is present
2. Specific text excerpts that support the doctrine
3. Explanation of how the doctrine is expressed
4. Any variations or evolution of the doctrine
5. Historical context if relevant

Format as JSON with keys: confidence_score, text_excerpts, explanation, evolution_notes, historical_context"""
        
        try:
            response = await self._generate_basic_response(prompt, self.system_prompt)
            
            # Parse JSON response
            import json
            try:
                analysis = json.loads(response)
                confidence = analysis.get('confidence_score', 0.0)
                
                # Only return if confidence is above threshold
                if confidence >= 0.3:
                    return {
                        'doctrine_name': definition.name,
                        'tradition': definition.tradition,
                        'denomination': definition.denomination,
                        'confidence_score': confidence,
                        'text_excerpts': analysis.get('text_excerpts', []),
                        'explanation': analysis.get('explanation', ''),
                        'evolution_notes': analysis.get('evolution_notes'),
                        'historical_context': analysis.get('historical_context')
                    }
            except json.JSONDecodeError:
                # Fallback to simple parsing if JSON fails
                confidence = self._extract_confidence_from_text(response)
                if confidence >= 0.3:
                    return {
                        'doctrine_name': definition.name,
                        'tradition': definition.tradition,
                        'denomination': definition.denomination,
                        'confidence_score': confidence,
                        'text_excerpts': [],
                        'explanation': response[:500],
                        'evolution_notes': None,
                        'historical_context': definition.historical_context
                    }
                    
        except Exception as e:
            self.logger.error(f"Error analyzing doctrine {doctrine_key}: {e}")
            
        return None
    
    def _extract_confidence_from_text(self, text: str) -> float:
        """Extract confidence score from text response."""
        import re
        
        # Look for confidence patterns
        patterns = [
            r'confidence[:\s]*([0-9]*\.?[0-9]+)',
            r'score[:\s]*([0-9]*\.?[0-9]+)',
            r'([0-9]*\.?[0-9]+)\s*(?:confidence|score)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    score = float(match.group(1))
                    return min(score, 1.0) if score <= 1.0 else score / 100.0
                except (ValueError, IndexError):
                    continue
        
        # Default confidence based on text content
        positive_indicators = ['clearly', 'evident', 'strong', 'explicit', 'obvious']
        negative_indicators = ['unclear', 'weak', 'absent', 'no evidence', 'doubtful']
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in text.lower())
        negative_count = sum(1 for indicator in negative_indicators if indicator in text.lower())
        
        if positive_count > negative_count:
            return 0.7
        elif negative_count > positive_count:
            return 0.2
        else:
            return 0.5
    
    async def _enhance_with_rag(
        self, 
        text: str, 
        doctrine_analysis: Dict[str, Any], 
        context_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance doctrine analysis with RAG insights."""
        doctrines = doctrine_analysis.get('doctrines', [])
        if not doctrines:
            return {}
        
        # Generate comparative analysis
        doctrine_names = [d['doctrine_name'] for d in doctrines]
        
        query = f"Compare these doctrines across different texts: {', '.join(doctrine_names)}"
        
        rag_response, citations = await self.generate_rag_response(
            query=query,
            context_texts=context_texts,
            system_prompt=self.system_prompt
        )
        
        return {
            'rag_enhancement': {
                'comparative_analysis': rag_response,
                'cross_textual_patterns': self._identify_cross_textual_patterns(doctrines, context_texts),
                'historical_development': self._trace_historical_development(doctrines, context_texts)
            }
        }
    
    def _identify_cross_textual_patterns(
        self, 
        doctrines: List[Dict[str, Any]], 
        context_texts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns across different texts."""
        patterns = []
        
        doctrine_by_tradition = defaultdict(list)
        for doctrine in doctrines:
            doctrine_by_tradition[doctrine['tradition']].append(doctrine)
        
        for tradition, tradition_doctrines in doctrine_by_tradition.items():
            if len(tradition_doctrines) > 1:
                patterns.append({
                    'pattern_type': 'tradition_consistency',
                    'tradition': tradition,
                    'description': f"Multiple {tradition} doctrines detected, suggesting doctrinal focus",
                    'doctrines': [d['doctrine_name'] for d in tradition_doctrines]
                })
        
        return patterns
    
    def _trace_historical_development(
        self, 
        doctrines: List[Dict[str, Any]], 
        context_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Trace historical development of doctrines."""
        development = {
            'timeline_analysis': [],
            'evolution_patterns': [],
            'contextual_influences': []
        }
        
        # Analyze temporal aspects
        for doctrine in doctrines:
            if doctrine.get('historical_context'):
                development['timeline_analysis'].append({
                    'doctrine': doctrine['doctrine_name'],
                    'historical_context': doctrine['historical_context'],
                    'tradition': doctrine['tradition']
                })
        
        return development
    
    def _analyze_cross_traditions(self, doctrines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze doctrines across different religious traditions."""
        traditions = set(d['tradition'] for d in doctrines)
        
        analysis = {
            'traditions_represented': list(traditions),
            'tradition_count': len(traditions),
            'doctrinal_overlaps': [],
            'unique_doctrines': []
        }
        
        # Find potential overlaps (similar concepts across traditions)
        overlaps = []
        for i, doctrine1 in enumerate(doctrines):
            for doctrine2 in doctrines[i+1:]:
                if (doctrine1['tradition'] != doctrine2['tradition'] and 
                    self._check_doctrinal_similarity(doctrine1, doctrine2)):
                    overlaps.append({
                        'doctrine1': doctrine1['doctrine_name'],
                        'tradition1': doctrine1['tradition'],
                        'doctrine2': doctrine2['doctrine_name'],
                        'tradition2': doctrine2['tradition'],
                        'similarity_type': 'conceptual'
                    })
        
        analysis['doctrinal_overlaps'] = overlaps
        
        return analysis
    
    def _check_doctrinal_similarity(self, doctrine1: Dict[str, Any], doctrine2: Dict[str, Any]) -> bool:
        """Check if two doctrines have conceptual similarity."""
        # Simple similarity check based on shared concepts
        concepts1 = set(doctrine1.get('explanation', '').lower().split())
        concepts2 = set(doctrine2.get('explanation', '').lower().split())
        
        common_concepts = concepts1.intersection(concepts2)
        
        # Consider similar if they share significant concepts
        similarity_threshold = 0.2
        union_size = len(concepts1.union(concepts2))
        
        return len(common_concepts) / union_size > similarity_threshold if union_size > 0 else False
    
    def _generate_analysis_summary(self, doctrines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of doctrine analysis."""
        if not doctrines:
            return {
                'total_doctrines': 0,
                'average_confidence': 0.0,
                'dominant_tradition': None,
                'doctrinal_diversity': 0.0
            }
        
        traditions = [d['tradition'] for d in doctrines]
        tradition_counts = defaultdict(int)
        
        total_confidence = sum(d['confidence_score'] for d in doctrines)
        
        for tradition in traditions:
            tradition_counts[tradition] += 1
        
        dominant_tradition = max(tradition_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_doctrines': len(doctrines),
            'average_confidence': total_confidence / len(doctrines),
            'dominant_tradition': dominant_tradition,
            'tradition_distribution': dict(tradition_counts),
            'doctrinal_diversity': len(set(traditions)) / len(doctrines),
            'high_confidence_doctrines': [
                d['doctrine_name'] for d in doctrines if d['confidence_score'] > 0.7
            ]
        }


# Backward compatibility alias
DoctrineAnalysisAgent = DoctrineAnalysisAgent
