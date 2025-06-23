"""Enhanced fallacy detection agent for identifying logical fallacies in spiritual texts with RAG integration."""

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
    """Enhanced agent for detecting logical fallacies in spiritual and religious texts with RAG integration."""
    
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
        "appeal_to_emotion": FallacyType(
            name="Appeal to Emotion",
            description="Using emotional manipulation instead of logical reasoning",
            examples=[
                "If you don't believe, you'll suffer eternally",
                "Think of how this will hurt your family"
            ],
            keywords=["suffer", "hurt", "fear", "think of", "emotional"]
        ),
        "bandwagon": FallacyType(
            name="Bandwagon",
            description="Claiming something is true because many people believe it",
            examples=[
                "Millions of believers can't be wrong",
                "Everyone in our community believes this"
            ],
            keywords=["everyone", "millions", "most people", "popular", "majority"]
        ),
        "no_true_scotsman": FallacyType(
            name="No True Scotsman",
            description="Dismissing counterexamples by redefining the group",
            examples=[
                "No true believer would act that way",
                "Real Christians don't doubt"
            ],
            keywords=["no true", "real", "authentic", "genuine"]
        )
    }
    
    def __init__(self):
        super().__init__(
            name="FallacyDetectionAgent",
            description="Detects and analyzes logical fallacies in spiritual and religious texts with RAG capabilities",
            enable_rag=True
        )
        
        # Build keyword index for efficient matching
        self.keyword_index = self._build_keyword_index()
        
        # System prompt for fallacy detection
        self.system_prompt = """You are an expert in logic, critical thinking, and argumentation analysis. 
        Your task is to identify logical fallacies in spiritual and religious texts while being respectful and objective.
        
        When analyzing text for fallacies:
        1. Identify specific logical fallacies present
        2. Provide confidence scores based on clear evidence
        3. Explain why the reasoning is fallacious
        4. Distinguish between legitimate religious discourse and actual logical errors
        5. Be respectful of religious beliefs while maintaining analytical rigor
        6. Consider the historical and cultural context
        
        Focus on the logical structure of arguments, not the religious content itself."""
    
    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """Build keyword index for efficient fallacy matching."""
        index = {}
        
        for fallacy_key, fallacy_type in self.FALLACY_TYPES.items():
            for keyword in fallacy_type.keywords:
                if keyword.lower() not in index:
                    index[keyword.lower()] = []
                index[keyword.lower()].append(fallacy_key)
                
        return index
    
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Process a fallacy detection query with RAG enhancement."""
        try:
            start_time = datetime.now()
            
            # Extract text from context or use query as text
            text = context.get('text', query) if context else query
            text_type = context.get('text_type') if context else None
            
            # Get relevant context using RAG if enabled
            context_texts = []
            if self.enable_rag and context and context.get('enable_rag', True):
                context_texts = await self.get_context_texts(
                    query=f"logical fallacy analysis: {query}",
                    text_types=[text_type] if text_type else None,
                    limit=3
                )
            
            # Perform fallacy detection
            fallacy_analysis = await self._analyze_fallacies(text, context_texts)
            
            # Store fallacy analysis results in database
            if fallacy_analysis['fallacies']:
                await self._store_fallacy_analysis(text, fallacy_analysis, context)
            
            # Generate enhanced analysis with RAG if context available
            if context_texts and fallacy_analysis['fallacies']:
                enhanced_analysis = await self._enhance_with_rag(
                    text, fallacy_analysis, context_texts
                )
                fallacy_analysis.update(enhanced_analysis)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=fallacy_analysis,
                metadata={
                    'agent_type': 'fallacy_detection',
                    'text_length': len(text),
                    'rag_context_used': len(context_texts),
                    'fallacies_detected': len(fallacy_analysis.get('fallacies', []))
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
            self.logger.error(f"Fallacy detection failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={}
            )
    
    async def _analyze_fallacies(self, text: str, context_texts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze text for logical fallacies."""
        # Initial keyword-based detection
        potential_fallacies = self._detect_potential_fallacies(text)
        
        # Enhanced analysis with LLM
        detected_fallacies = []
        for fallacy_key in potential_fallacies:
            fallacy_analysis = await self._analyze_specific_fallacy(text, fallacy_key, context_texts)
            if fallacy_analysis:
                detected_fallacies.append(fallacy_analysis)
        
        # Pattern-based detection for common fallacy patterns
        pattern_fallacies = await self._detect_pattern_fallacies(text, context_texts)
        detected_fallacies.extend(pattern_fallacies)
        
        # Remove duplicates and merge similar detections
        unique_fallacies = self._merge_similar_fallacies(detected_fallacies)
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(unique_fallacies)
        
        return {
            'fallacies': unique_fallacies,
            'analysis_summary': analysis_summary,
            'total_fallacies_detected': len(unique_fallacies),
            'fallacy_categories': self._categorize_fallacies(unique_fallacies)
        }
    
    def _detect_potential_fallacies(self, text: str) -> List[str]:
        """Detect potential fallacies based on keyword matching."""
        text_lower = text.lower()
        potential_fallacies = set()
        
        for keyword, fallacy_keys in self.keyword_index.items():
            if keyword in text_lower:
                potential_fallacies.update(fallacy_keys)
        
        return list(potential_fallacies)
    
    async def _analyze_specific_fallacy(
        self, 
        text: str, 
        fallacy_key: str, 
        context_texts: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze specific fallacy in text with LLM enhancement."""
        fallacy_type = self.FALLACY_TYPES[fallacy_key]
        
        # Prepare context information
        context_info = ""
        if context_texts:
            context_info = "\n\nRelevant context from similar texts:\n" + "\n".join([
                f"- {ctx['title']}: {ctx['content'][:200]}..."
                for ctx in context_texts[:2]
            ])
        
        prompt = f"""Analyze the following text for the logical fallacy "{fallacy_type.name}":

Fallacy Definition:
- Name: {fallacy_type.name}
- Description: {fallacy_type.description}
- Keywords: {', '.join(fallacy_type.keywords)}
- Examples: {'; '.join(fallacy_type.examples)}

Text to analyze:
{text[:2000]}...

{context_info}

Please provide:
1. Confidence score (0.0-1.0) that this fallacy is present
2. Specific text excerpts that demonstrate the fallacy
3. Explanation of why this constitutes the fallacy
4. Context of the argument structure
5. Severity assessment (minor, moderate, major)

Format as JSON with keys: confidence_score, text_excerpts, explanation, context, severity"""
        
        try:
            response = await self._generate_basic_response(prompt, self.system_prompt)
            
            # Parse JSON response
            import json
            try:
                analysis = json.loads(response)
                confidence = analysis.get('confidence_score', 0.0)
                
                # Only return if confidence is above threshold
                if confidence >= 0.4:  # Higher threshold for fallacies to avoid false positives
                    return {
                        'fallacy_type': fallacy_type.name,
                        'confidence_score': confidence,
                        'text_excerpts': analysis.get('text_excerpts', []),
                        'explanation': analysis.get('explanation', ''),
                        'context': analysis.get('context', ''),
                        'severity': analysis.get('severity', 'moderate'),
                        'keywords_matched': [kw for kw in fallacy_type.keywords if kw.lower() in text.lower()]
                    }
            except json.JSONDecodeError:
                # Fallback to simple parsing if JSON fails
                confidence = self._extract_confidence_from_text(response)
                if confidence >= 0.4:
                    return {
                        'fallacy_type': fallacy_type.name,
                        'confidence_score': confidence,
                        'text_excerpts': [],
                        'explanation': response[:500],
                        'context': 'Detected through keyword analysis',
                        'severity': 'moderate',
                        'keywords_matched': [kw for kw in fallacy_type.keywords if kw.lower() in text.lower()]
                    }
                    
        except Exception as e:
            self.logger.error(f"Error analyzing fallacy {fallacy_key}: {e}")
            
        return None
    
    async def _detect_pattern_fallacies(self, text: str, context_texts: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect fallacies using pattern recognition."""
        pattern_fallacies = []
        
        # Pattern for circular reasoning
        circular_patterns = [
            r"because.*it says.*so",
            r"proves itself",
            r"self.*evident.*truth"
        ]
        
        for pattern in circular_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_fallacies.append({
                    'fallacy_type': 'Circular Reasoning',
                    'confidence_score': 0.6,
                    'text_excerpts': [self._extract_pattern_context(text, pattern)],
                    'explanation': 'Detected circular reasoning pattern in argument structure',
                    'context': 'Pattern-based detection',
                    'severity': 'moderate',
                    'keywords_matched': []
                })
        
        # Pattern for false dichotomy
        dichotomy_patterns = [
            r"either.*or",
            r"only.*two.*choices",
            r"must.*choose.*between"
        ]
        
        for pattern in dichotomy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_fallacies.append({
                    'fallacy_type': 'False Dichotomy',
                    'confidence_score': 0.5,
                    'text_excerpts': [self._extract_pattern_context(text, pattern)],
                    'explanation': 'Detected false dichotomy pattern limiting options artificially',
                    'context': 'Pattern-based detection',
                    'severity': 'moderate',
                    'keywords_matched': []
                })
        
        return pattern_fallacies
    
    def _extract_pattern_context(self, text: str, pattern: str) -> str:
        """Extract context around a pattern match."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            return text[start:end].strip()
        return ""
    
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
        strong_indicators = ['clearly', 'obvious', 'definite', 'certain', 'undoubtedly']
        weak_indicators = ['possibly', 'might', 'unclear', 'uncertain', 'doubtful']
        
        strong_count = sum(1 for indicator in strong_indicators if indicator in text.lower())
        weak_count = sum(1 for indicator in weak_indicators if indicator in text.lower())
        
        if strong_count > weak_count:
            return 0.7
        elif weak_count > strong_count:
            return 0.3
        else:
            return 0.5
    
    def _merge_similar_fallacies(self, fallacies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge similar fallacy detections to avoid duplicates."""
        if not fallacies:
            return []
        
        merged = []
        processed_types = set()
        
        for fallacy in sorted(fallacies, key=lambda x: x['confidence_score'], reverse=True):
            fallacy_type = fallacy['fallacy_type']
            
            if fallacy_type not in processed_types:
                # Find all fallacies of this type
                same_type = [f for f in fallacies if f['fallacy_type'] == fallacy_type]
                
                if len(same_type) == 1:
                    merged.append(fallacy)
                else:
                    # Merge multiple detections of the same type
                    best_confidence = max(f['confidence_score'] for f in same_type)
                    all_excerpts = []
                    all_explanations = []
                    
                    for f in same_type:
                        all_excerpts.extend(f.get('text_excerpts', []))
                        all_explanations.append(f.get('explanation', ''))
                    
                    merged_fallacy = {
                        'fallacy_type': fallacy_type,
                        'confidence_score': best_confidence,
                        'text_excerpts': list(set(all_excerpts))[:3],  # Limit to 3 unique excerpts
                        'explanation': '; '.join(set(all_explanations)),
                        'context': same_type[0].get('context', ''),
                        'severity': same_type[0].get('severity', 'moderate'),
                        'keywords_matched': list(set().union(*[f.get('keywords_matched', []) for f in same_type]))
                    }
                    merged.append(merged_fallacy)
                
                processed_types.add(fallacy_type)
        
        return merged
    
    def _categorize_fallacies(self, fallacies: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize fallacies by type for analysis."""
        categories = {
            'formal': [],
            'informal': [],
            'emotional': [],
            'authority': []
        }
        
        for fallacy in fallacies:
            fallacy_type = fallacy['fallacy_type']
            
            if fallacy_type in ['Circular Reasoning']:
                categories['formal'].append(fallacy_type)
            elif fallacy_type in ['Appeal to Emotion']:
                categories['emotional'].append(fallacy_type)
            elif fallacy_type in ['Appeal to Authority']:
                categories['authority'].append(fallacy_type)
            else:
                categories['informal'].append(fallacy_type)
        
        return {k: v for k, v in categories.items() if v}  # Remove empty categories
    
    def _generate_analysis_summary(self, fallacies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of fallacy analysis."""
        if not fallacies:
            return {
                'total_fallacies': 0,
                'average_confidence': 0.0,
                'most_common_fallacy': None,
                'overall_logical_quality': 'good'
            }
        
        total_confidence = sum(f['confidence_score'] for f in fallacies)
        fallacy_types = [f['fallacy_type'] for f in fallacies]
        
        # Count occurrences
        from collections import Counter
        type_counts = Counter(fallacy_types)
        most_common = type_counts.most_common(1)[0] if type_counts else None
        
        # Assess overall logical quality
        avg_confidence = total_confidence / len(fallacies)
        if avg_confidence > 0.7 and len(fallacies) > 3:
            quality = 'poor'
        elif avg_confidence > 0.5 and len(fallacies) > 1:
            quality = 'fair'
        elif len(fallacies) == 0:
            quality = 'good'
        else:
            quality = 'acceptable'
        
        return {
            'total_fallacies': len(fallacies),
            'average_confidence': avg_confidence,
            'most_common_fallacy': most_common[0] if most_common else None,
            'fallacy_distribution': dict(type_counts),
            'overall_logical_quality': quality,
            'high_confidence_fallacies': [
                f['fallacy_type'] for f in fallacies if f['confidence_score'] > 0.7
            ]
        }
    
    async def _store_fallacy_analysis(
        self, 
        text: str, 
        analysis: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ):
        """Store fallacy analysis results in the database."""
        try:
            # This will be implemented once we have the fallacy analysis table
            # For now, we'll log the results
            self.logger.info(f"Fallacy analysis completed: {len(analysis['fallacies'])} fallacies detected")
            
            # TODO: Implement database storage for fallacy analysis results
            # This should store results in a separate table specifically for analysis results
            
        except Exception as e:
            self.logger.error(f"Failed to store fallacy analysis: {e}")
    
    async def _enhance_with_rag(
        self, 
        text: str, 
        fallacy_analysis: Dict[str, Any], 
        context_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance fallacy analysis with RAG insights."""
        fallacies = fallacy_analysis.get('fallacies', [])
        if not fallacies:
            return {}
        
        # Generate comparative analysis
        fallacy_types = [f['fallacy_type'] for f in fallacies]
        
        query = f"Analyze the logical structure and fallacies in similar texts: {', '.join(fallacy_types)}"
        
        rag_response, citations = await self.generate_rag_response(
            query=query,
            context_texts=context_texts,
            system_prompt=self.system_prompt
        )
        
        return {
            'rag_enhancement': {
                'comparative_fallacy_analysis': rag_response,
                'cross_textual_patterns': self._identify_cross_textual_patterns(fallacies, context_texts),
                'logical_quality_comparison': self._compare_logical_quality(fallacies, context_texts)
            }
        }
    
    def _identify_cross_textual_patterns(
        self, 
        fallacies: List[Dict[str, Any]], 
        context_texts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns across different texts."""
        patterns = []
        
        fallacy_by_type = {}
        for fallacy in fallacies:
            ftype = fallacy['fallacy_type']
            if ftype not in fallacy_by_type:
                fallacy_by_type[ftype] = []
            fallacy_by_type[ftype].append(fallacy)
        
        for fallacy_type, type_fallacies in fallacy_by_type.items():
            if len(type_fallacies) > 1:
                patterns.append({
                    'pattern_type': 'repeated_fallacy',
                    'fallacy_type': fallacy_type,
                    'description': f"Multiple instances of {fallacy_type} detected, suggesting systematic logical issues",
                    'frequency': len(type_fallacies)
                })
        
        return patterns
    
    def _compare_logical_quality(
        self, 
        fallacies: List[Dict[str, Any]], 
        context_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare logical quality with context texts."""
        current_quality = self._calculate_logical_quality_score(fallacies)
        
        return {
            'current_logical_quality_score': current_quality,
            'quality_assessment': self._assess_quality_level(current_quality),
            'improvement_suggestions': self._generate_improvement_suggestions(fallacies)
        }
    
    def _calculate_logical_quality_score(self, fallacies: List[Dict[str, Any]]) -> float:
        """Calculate a logical quality score (0-100)."""
        if not fallacies:
            return 95.0
        
        # Start with perfect score and deduct for fallacies
        score = 100.0
        
        for fallacy in fallacies:
            confidence = fallacy['confidence_score']
            severity = fallacy.get('severity', 'moderate')
            
            # Deduct points based on confidence and severity
            if severity == 'major':
                deduction = confidence * 15
            elif severity == 'moderate':
                deduction = confidence * 10
            else:  # minor
                deduction = confidence * 5
            
            score -= deduction
        
        return max(score, 0.0)
    
    def _assess_quality_level(self, score: float) -> str:
        """Assess logical quality level based on score."""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'very_poor'
    
    def _generate_improvement_suggestions(self, fallacies: List[Dict[str, Any]]) -> List[str]:
        """Generate suggestions for improving logical quality."""
        if not fallacies:
            return ["The text demonstrates good logical reasoning."]
        
        suggestions = []
        fallacy_types = set(f['fallacy_type'] for f in fallacies)
        
        if 'Ad Hominem' in fallacy_types:
            suggestions.append("Focus on addressing arguments rather than attacking individuals or groups.")
        
        if 'Straw Man' in fallacy_types:
            suggestions.append("Ensure you're addressing opponents' actual positions, not simplified versions.")
        
        if 'False Dichotomy' in fallacy_types:
            suggestions.append("Consider additional options beyond the presented alternatives.")
        
        if 'Circular Reasoning' in fallacy_types:
            suggestions.append("Provide independent evidence rather than using conclusions as premises.")
        
        if 'Appeal to Authority' in fallacy_types:
            suggestions.append("Support authoritative claims with additional evidence and reasoning.")
        
        if 'Appeal to Emotion' in fallacy_types:
            suggestions.append("Balance emotional appeals with logical reasoning and evidence.")
        
        return suggestions
