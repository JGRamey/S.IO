"""Translation tracking agent for monitoring text translations across languages."""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

from solomon.config import settings
from solomon.database.models import Language
from .base import BaseAgent, AgentResult


class TranslationChain(BaseModel):
    """Structure for tracking translation chains."""
    original_language: str
    target_language: str
    chain: List[str]  # Languages in translation chain
    accuracy_score: Optional[float] = None
    notes: Optional[str] = None


class TranslationIssue(BaseModel):
    """Structure for translation issues or discrepancies."""
    issue_type: str  # mistranslation, cultural_bias, linguistic_drift, etc.
    description: str
    original_text: str
    translated_text: str
    severity: str  # low, medium, high
    explanation: str


class TranslationAnalysis(BaseModel):
    """Structure for comprehensive translation analysis."""
    source_language: str
    target_language: str
    translation_chain: List[str]
    accuracy_assessment: float
    issues_found: List[TranslationIssue]
    linguistic_notes: str
    cultural_context: str


class TranslationTrackingAgent(BaseAgent):
    """Agent for tracking and analyzing text translations across languages."""
    
    COMMON_TRANSLATION_CHAINS = {
        "hebrew_to_english": ["Hebrew", "Greek", "Latin", "English"],
        "aramaic_to_english": ["Aramaic", "Greek", "Latin", "English"],
        "arabic_to_english": ["Arabic", "Latin", "English"],
        "sanskrit_to_english": ["Sanskrit", "English"],
        "greek_to_english": ["Greek", "Latin", "English"],
    }
    
    TRANSLATION_ISSUES = {
        "mistranslation": "Incorrect translation of words or phrases",
        "cultural_bias": "Translation influenced by translator's cultural background",
        "linguistic_drift": "Meaning changes through multiple translation steps",
        "anachronism": "Modern concepts imposed on ancient texts",
        "theological_bias": "Translation influenced by doctrinal preferences",
        "gender_bias": "Gendered language choices affecting meaning",
        "political_influence": "Translation influenced by political considerations",
        "manuscript_variants": "Different source manuscripts leading to different translations"
    }
    
    def __init__(self):
        super().__init__(
            name="translation_tracking",
            description="Tracks and analyzes translations of spiritual texts across languages"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute translation tracking analysis."""
        try:
            original_text = input_data.get("original_text", "")
            translated_text = input_data.get("translated_text", "")
            source_language = input_data.get("source_language", "")
            target_language = input_data.get("target_language", "")
            translation_chain = input_data.get("translation_chain", [])
            text_id = input_data.get("text_id")
            
            if not original_text or not translated_text:
                return self._create_result(
                    success=False,
                    error="Both original_text and translated_text are required"
                )
            
            # Analyze the translation
            analysis = await self._analyze_translation(
                original_text, translated_text, source_language, target_language, translation_chain
            )
            
            # Detect translation issues
            issues = await self._detect_translation_issues(
                original_text, translated_text, source_language, target_language
            )
            
            # Assess translation accuracy
            accuracy_score = await self._assess_translation_accuracy(
                original_text, translated_text, source_language, target_language
            )
            
            # Track linguistic evolution if chain provided
            evolution_analysis = await self._track_linguistic_evolution(
                translation_chain, original_text, translated_text
            ) if translation_chain else {}
            
            return self._create_result(
                success=True,
                data={
                    "text_id": text_id,
                    "source_language": source_language,
                    "target_language": target_language,
                    "translation_chain": translation_chain,
                    "accuracy_score": accuracy_score,
                    "analysis": analysis.dict() if analysis else {},
                    "issues_detected": len(issues),
                    "issues": [issue.dict() for issue in issues],
                    "evolution_analysis": evolution_analysis,
                    "summary": self._create_summary(analysis, issues, accuracy_score)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Translation tracking failed: {e}")
            return self._create_result(
                success=False,
                error=str(e)
            )
    
    async def _analyze_translation(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        translation_chain: List[str] = None
    ) -> Optional[TranslationAnalysis]:
        """Perform comprehensive translation analysis."""
        try:
            system_prompt = """You are an expert linguist and translator specializing in ancient and religious texts. 
            Your task is to analyze the quality and accuracy of translations, identifying potential issues and providing insights into the translation process.
            
            Focus on:
            1. Accuracy of word choices and meanings
            2. Cultural and contextual appropriateness
            3. Preservation of original intent
            4. Identification of potential biases
            5. Linguistic and theological implications"""
            
            chain_context = f"Translation chain: {' → '.join(translation_chain)}" if translation_chain else ""
            
            analysis_prompt = f"""Analyze this translation from {source_language} to {target_language}:

{chain_context}

Original text ({source_language}):
{original_text}

Translated text ({target_language}):
{translated_text}

Provide analysis covering:
1. Overall translation accuracy (score 0.0-1.0)
2. Key linguistic choices and their implications
3. Cultural context considerations
4. Any potential issues or biases
5. Suggestions for improvement

Respond in JSON format:
{{
  "accuracy_score": 0.8,
  "linguistic_notes": "analysis of key translation choices",
  "cultural_context": "cultural considerations",
  "key_issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"]
}}"""
            
            response = await self._analyze_text(original_text, analysis_prompt, system_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                
                return TranslationAnalysis(
                    source_language=source_language,
                    target_language=target_language,
                    translation_chain=translation_chain or [],
                    accuracy_assessment=result.get("accuracy_score", 0.5),
                    issues_found=[],  # Will be populated by separate issue detection
                    linguistic_notes=result.get("linguistic_notes", ""),
                    cultural_context=result.get("cultural_context", "")
                )
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse LLM JSON response for translation analysis")
                return None
                
        except Exception as e:
            self.logger.error(f"Translation analysis failed: {e}")
            return None
    
    async def _detect_translation_issues(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> List[TranslationIssue]:
        """Detect specific translation issues."""
        issues = []
        
        # Method 1: Pattern-based detection
        pattern_issues = self._detect_issues_by_patterns(original_text, translated_text)
        issues.extend(pattern_issues)
        
        # Method 2: LLM-based issue detection
        llm_issues = await self._detect_issues_by_llm(
            original_text, translated_text, source_language, target_language
        )
        issues.extend(llm_issues)
        
        # Method 3: Linguistic analysis
        linguistic_issues = self._detect_linguistic_issues(
            original_text, translated_text, source_language, target_language
        )
        issues.extend(linguistic_issues)
        
        return self._merge_similar_issues(issues)
    
    def _detect_issues_by_patterns(
        self,
        original_text: str,
        translated_text: str
    ) -> List[TranslationIssue]:
        """Detect issues using pattern matching."""
        issues = []
        
        # Check for gender bias patterns
        gender_patterns = [
            (r'\bhe\b', r'\bshe\b'),
            (r'\bhim\b', r'\bher\b'),
            (r'\bhis\b', r'\bhers?\b'),
            (r'\bman\b', r'\bwoman\b'),
            (r'\bmen\b', r'\bwomen\b'),
        ]
        
        for male_pattern, female_pattern in gender_patterns:
            male_count = len(re.findall(male_pattern, translated_text, re.IGNORECASE))
            female_count = len(re.findall(female_pattern, translated_text, re.IGNORECASE))
            
            if male_count > 0 and female_count == 0:
                issues.append(TranslationIssue(
                    issue_type="gender_bias",
                    description="Translation uses exclusively masculine language",
                    original_text=original_text[:100] + "...",
                    translated_text=translated_text[:100] + "...",
                    severity="medium",
                    explanation="Consider if original text was gender-neutral or inclusive"
                ))
        
        # Check for anachronistic terms
        modern_terms = [
            "computer", "internet", "technology", "democracy", "capitalism",
            "psychology", "science", "evolution", "genetics"
        ]
        
        for term in modern_terms:
            if term.lower() in translated_text.lower():
                issues.append(TranslationIssue(
                    issue_type="anachronism",
                    description=f"Modern term '{term}' used in ancient text translation",
                    original_text=original_text[:100] + "...",
                    translated_text=translated_text[:100] + "...",
                    severity="high",
                    explanation="Modern concepts may not accurately represent ancient ideas"
                ))
        
        return issues
    
    async def _detect_issues_by_llm(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> List[TranslationIssue]:
        """Detect translation issues using LLM analysis."""
        try:
            system_prompt = """You are an expert in translation criticism and linguistic analysis. 
            Identify potential issues in the provided translation, including:
            
            1. Mistranslations - incorrect word choices
            2. Cultural bias - translator's cultural assumptions
            3. Theological bias - doctrinal influences on translation
            4. Linguistic drift - meaning changes through translation chain
            5. Gender bias - inappropriate gendered language choices
            6. Anachronisms - modern concepts in ancient texts
            7. Political influence - political considerations affecting translation
            
            For each issue, assess its severity (low/medium/high)."""
            
            analysis_prompt = f"""Identify translation issues in this {source_language} to {target_language} translation:

Original ({source_language}):
{original_text}

Translation ({target_language}):
{translated_text}

Identify specific issues and respond in JSON format:
{{
  "issues": [
    {{
      "type": "issue_type",
      "description": "brief description",
      "original_excerpt": "relevant original text",
      "translated_excerpt": "relevant translated text", 
      "severity": "low/medium/high",
      "explanation": "detailed explanation of the issue"
    }}
  ]
}}"""
            
            response = await self._analyze_text(original_text, analysis_prompt, system_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                issues = []
                
                for issue_data in result.get("issues", []):
                    issues.append(TranslationIssue(
                        issue_type=issue_data.get("type", "unknown"),
                        description=issue_data.get("description", ""),
                        original_text=issue_data.get("original_excerpt", ""),
                        translated_text=issue_data.get("translated_excerpt", ""),
                        severity=issue_data.get("severity", "medium"),
                        explanation=issue_data.get("explanation", "")
                    ))
                
                return issues
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse LLM JSON response for issue detection")
                return []
                
        except Exception as e:
            self.logger.error(f"LLM issue detection failed: {e}")
            return []
    
    def _detect_linguistic_issues(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> List[TranslationIssue]:
        """Detect linguistic issues through analysis."""
        issues = []
        
        # Check for significant length differences (may indicate over/under translation)
        orig_words = len(original_text.split())
        trans_words = len(translated_text.split())
        
        if orig_words > 0:
            ratio = trans_words / orig_words
            
            if ratio > 2.0:
                issues.append(TranslationIssue(
                    issue_type="over_translation",
                    description="Translation is significantly longer than original",
                    original_text=f"Original: {orig_words} words",
                    translated_text=f"Translation: {trans_words} words",
                    severity="medium",
                    explanation="May indicate explanatory additions or verbose translation style"
                ))
            elif ratio < 0.5:
                issues.append(TranslationIssue(
                    issue_type="under_translation",
                    description="Translation is significantly shorter than original",
                    original_text=f"Original: {orig_words} words",
                    translated_text=f"Translation: {trans_words} words",
                    severity="medium",
                    explanation="May indicate omissions or overly concise translation"
                ))
        
        # Check for repetitive patterns (may indicate translation artifacts)
        words = translated_text.lower().split()
        word_counts = defaultdict(int)
        for word in words:
            if len(word) > 3:  # Skip short words
                word_counts[word] += 1
        
        highly_repeated = [word for word, count in word_counts.items() if count > len(words) * 0.1]
        if highly_repeated:
            issues.append(TranslationIssue(
                issue_type="repetitive_translation",
                description="Unusual repetition of certain words",
                original_text="",
                translated_text=f"Repeated words: {', '.join(highly_repeated)}",
                severity="low",
                explanation="May indicate translation artifacts or limited vocabulary choices"
            ))
        
        return issues
    
    async def _assess_translation_accuracy(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Assess overall translation accuracy."""
        try:
            system_prompt = """You are an expert translator and linguist. 
            Assess the accuracy of the provided translation on a scale from 0.0 to 1.0, where:
            - 1.0 = Perfect translation preserving all meaning and nuance
            - 0.8-0.9 = Very good translation with minor issues
            - 0.6-0.7 = Good translation with some meaning preserved
            - 0.4-0.5 = Adequate translation but significant issues
            - 0.2-0.3 = Poor translation with major problems
            - 0.0-0.1 = Very poor or completely incorrect translation
            
            Consider accuracy of meaning, cultural context, and linguistic appropriateness."""
            
            analysis_prompt = f"""Rate the accuracy of this {source_language} to {target_language} translation:

Original ({source_language}):
{original_text}

Translation ({target_language}):
{translated_text}

Provide only a numeric accuracy score between 0.0 and 1.0."""
            
            response = await self._analyze_text(original_text, analysis_prompt, system_prompt)
            
            # Extract numeric score
            score_match = re.search(r'(\d+\.?\d*)', response)
            if score_match:
                score = float(score_match.group(1))
                return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
            
            return 0.5  # Default if no score found
            
        except Exception as e:
            self.logger.error(f"Translation accuracy assessment failed: {e}")
            return 0.5
    
    async def _track_linguistic_evolution(
        self,
        translation_chain: List[str],
        original_text: str,
        final_text: str
    ) -> Dict[str, Any]:
        """Track how meaning evolved through translation chain."""
        if len(translation_chain) < 2:
            return {}
        
        try:
            system_prompt = """You are an expert in historical linguistics and translation studies. 
            Analyze how meaning and interpretation may have evolved through a chain of translations."""
            
            chain_str = " → ".join(translation_chain)
            
            analysis_prompt = f"""Analyze the linguistic evolution through this translation chain:

Translation chain: {chain_str}

Original text: {original_text}
Final translation: {final_text}

Describe:
1. How meaning might have shifted at each translation step
2. Cultural influences that may have affected translations
3. Linguistic features that may have been lost or added
4. Overall assessment of meaning preservation

Provide a brief analysis of the evolution process."""
            
            response = await self._analyze_text(original_text, analysis_prompt, system_prompt)
            
            return {
                "translation_chain": translation_chain,
                "evolution_analysis": response,
                "chain_length": len(translation_chain),
                "potential_drift": "high" if len(translation_chain) > 3 else "medium" if len(translation_chain) > 2 else "low"
            }
            
        except Exception as e:
            self.logger.error(f"Linguistic evolution tracking failed: {e}")
            return {}
    
    def _merge_similar_issues(self, issues: List[TranslationIssue]) -> List[TranslationIssue]:
        """Merge similar translation issues."""
        issue_groups = defaultdict(list)
        
        # Group by issue type
        for issue in issues:
            issue_groups[issue.issue_type].append(issue)
        
        merged = []
        for issue_type, group_issues in issue_groups.items():
            if len(group_issues) == 1:
                merged.append(group_issues[0])
            else:
                # Merge similar issues
                best_issue = max(group_issues, key=lambda i: len(i.explanation))
                
                # Combine descriptions
                all_descriptions = [issue.description for issue in group_issues]
                combined_description = "; ".join(set(all_descriptions))
                
                merged_issue = TranslationIssue(
                    issue_type=issue_type,
                    description=combined_description,
                    original_text=best_issue.original_text,
                    translated_text=best_issue.translated_text,
                    severity=best_issue.severity,
                    explanation=best_issue.explanation
                )
                merged.append(merged_issue)
        
        return merged
    
    def _create_summary(
        self,
        analysis: Optional[TranslationAnalysis],
        issues: List[TranslationIssue],
        accuracy_score: float
    ) -> Dict[str, Any]:
        """Create a summary of translation analysis."""
        severity_counts = defaultdict(int)
        issue_types = defaultdict(int)
        
        for issue in issues:
            severity_counts[issue.severity] += 1
            issue_types[issue.issue_type] += 1
        
        quality_assessment = "excellent" if accuracy_score >= 0.9 else \
                           "very good" if accuracy_score >= 0.8 else \
                           "good" if accuracy_score >= 0.7 else \
                           "fair" if accuracy_score >= 0.6 else \
                           "poor"
        
        return {
            "accuracy_score": round(accuracy_score, 2),
            "quality_assessment": quality_assessment,
            "total_issues": len(issues),
            "severity_breakdown": dict(severity_counts),
            "issue_types": dict(issue_types),
            "has_analysis": analysis is not None,
            "message": f"Translation quality: {quality_assessment} ({len(issues)} issues found)"
        }
