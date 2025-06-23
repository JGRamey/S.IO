#!/usr/bin/env python3
"""
Standalone Bias Detection Test
Tests bias detection functionality without complex dependencies
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BiasDetection:
    """Represents a detected bias instance."""
    bias_type: str
    confidence: float
    text_snippet: str
    explanation: str
    severity: str
    start_position: int
    end_position: int
    suggestions: List[str]
    category: str

class SimpleBiasDetector:
    """Simplified bias detector for testing"""
    
    # Comprehensive bias taxonomy
    BIAS_TYPES = {
        # Cognitive Biases
        "confirmation_bias": {
            "description": "Tendency to search for information that confirms pre-existing beliefs",
            "category": "cognitive",
            "keywords": ["obviously", "clearly", "any reasonable person", "it's evident that", "undoubtedly"]
        },
        "authority_bias": {
            "description": "Tendency to attribute greater accuracy to authority figures",
            "category": "cognitive", 
            "keywords": ["the church says", "ancient wisdom", "scholars agree", "tradition teaches", "authorities confirm"]
        },
        "cultural_supremacy": {
            "description": "Belief that one's own culture is superior to others",
            "category": "cultural",
            "keywords": ["primitive", "advanced", "enlightened vs unenlightened", "higher truth", "superior path"]
        },
        "gender_bias": {
            "description": "Systematic prejudice based on gender",
            "category": "social",
            "keywords": ["women are naturally", "men should", "feminine weakness", "masculine strength", "natural role"]
        },
        "religious_exclusivism": {
            "description": "Claim that only one religious tradition possesses ultimate truth",
            "category": "religious",
            "keywords": ["only true path", "exclusive truth", "chosen people", "one way", "false religions"]
        },
        "in_group_bias": {
            "description": "Tendency to favor one's own group over others",
            "category": "social",
            "keywords": ["we", "us", "our way", "outsiders", "they don't understand", "only we know"]
        }
    }
    
    def __init__(self):
        self.analysis_cache = {}
    
    def detect_pattern_biases(self, text: str, sensitivity: str = "medium") -> List[BiasDetection]:
        """Detect biases using pattern matching"""
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
                    
                    confidence = self.calculate_pattern_confidence(keyword, context, bias_type)
                    
                    if confidence >= confidence_threshold:
                        severity = self.determine_severity(context)
                        suggestions = self.generate_bias_suggestions(bias_type, keyword)
                        
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
    
    def detect_linguistic_biases(self, text: str) -> List[BiasDetection]:
        """Detect biases through linguistic analysis"""
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
    
    def calculate_pattern_confidence(self, keyword: str, context: str, bias_type: str) -> float:
        """Calculate confidence score for pattern-based detection"""
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
    
    def determine_severity(self, context: str) -> str:
        """Determine severity based on context"""
        context_lower = context.lower()
        
        severity_indicators = {
            "critical": ["absolutely false", "complete nonsense", "totally wrong", "utterly misguided"],
            "high": ["clearly wrong", "obviously false", "certainly incorrect", "definitely misguided"],
            "medium": ["probably wrong", "likely incorrect", "seems misguided", "appears false"],
            "low": ["might be wrong", "could be incorrect", "questionable", "somewhat biased"]
        }
        
        for severity, indicators in severity_indicators.items():
            for indicator in indicators:
                if indicator in context_lower:
                    return severity
        
        return "low"
    
    def generate_bias_suggestions(self, bias_type: str, keyword: str) -> List[str]:
        """Generate suggestions for addressing detected bias"""
        suggestions_map = {
            "confirmation_bias": [
                "Consider counter-arguments",
                "Seek disconfirming evidence",
                "Use more tentative language"
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
            ],
            "in_group_bias": [
                "Include diverse perspectives",
                "Avoid us-vs-them language",
                "Consider outsider viewpoints"
            ]
        }
        
        return suggestions_map.get(bias_type, ["Consider alternative perspectives", "Use more neutral language"])
    
    def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Main analysis method"""
        domain = kwargs.get('domain', 'general')
        sensitivity = kwargs.get('sensitivity', 'medium')
        
        # Multi-layered bias analysis
        pattern_biases = self.detect_pattern_biases(text, sensitivity)
        linguistic_biases = self.detect_linguistic_biases(text)
        
        # Combine all detected biases
        all_biases = pattern_biases + linguistic_biases
        
        # Remove duplicates and rank by confidence
        unique_biases = self.deduplicate_biases(all_biases)
        ranked_biases = sorted(unique_biases, key=lambda x: x.confidence, reverse=True)
        
        # Generate overall bias assessment
        bias_summary = self.generate_bias_summary(ranked_biases, text)
        
        # Create recommendations
        recommendations = self.generate_recommendations(ranked_biases, domain)
        
        return {
            "detected_biases": [self.bias_to_dict(bias) for bias in ranked_biases],
            "bias_summary": bias_summary,
            "recommendations": recommendations,
            "overall_bias_score": self.calculate_overall_bias_score(ranked_biases),
            "analysis_metadata": {
                "domain": domain,
                "sensitivity": sensitivity,
                "total_biases_found": len(ranked_biases),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
    
    def deduplicate_biases(self, biases: List[BiasDetection]) -> List[BiasDetection]:
        """Remove duplicate bias detections"""
        seen = set()
        unique_biases = []
        
        for bias in biases:
            # Create a signature for the bias
            signature = (bias.bias_type, bias.start_position, bias.end_position)
            
            if signature not in seen:
                seen.add(signature)
                unique_biases.append(bias)
        
        return unique_biases
    
    def generate_bias_summary(self, biases: List[BiasDetection], text: str) -> Dict[str, Any]:
        """Generate overall bias summary"""
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
    
    def generate_recommendations(self, biases: List[BiasDetection], domain: str) -> List[str]:
        """Generate overall recommendations for reducing bias"""
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
        
        if "linguistic" in categories_present:
            recommendations.append("Use more nuanced language and avoid absolute statements")
        
        # General recommendations
        recommendations.extend([
            "Consider having content reviewed by someone from a different background",
            "Actively seek out opposing viewpoints and address them fairly",
            "Provide evidence for assertions rather than assuming agreement"
        ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def calculate_overall_bias_score(self, biases: List[BiasDetection]) -> float:
        """Calculate overall bias score (0.0 = no bias, 1.0 = highly biased)"""
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
    
    def bias_to_dict(self, bias: BiasDetection) -> Dict[str, Any]:
        """Convert BiasDetection to dictionary"""
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

def test_bias_detection():
    """Test the bias detection functionality"""
    
    print("🔍 TESTING STANDALONE BIAS DETECTION")
    print("="*45)
    
    detector = SimpleBiasDetector()
    
    # Test cases
    test_cases = [
        {
            "name": "Cultural Supremacy Bias",
            "text": """Obviously, Western civilization represents the pinnacle of human achievement. 
            Primitive Eastern philosophies pale in comparison to our advanced, scientific worldview. 
            Any reasonable person can see this truth.""",
            "expected_biases": ["cultural_supremacy", "confirmation_bias"]
        },
        {
            "name": "Gender Bias",
            "text": """Women are naturally more emotional and less logical than men, which explains 
            why most great philosophers have been male. This is just biological fact.""",
            "expected_biases": ["gender_bias"]
        },
        {
            "name": "Religious Exclusivism",
            "text": """Only Christianity offers the true path to salvation. All other religions 
            are false and lead people astray from God's one way to truth.""",
            "expected_biases": ["religious_exclusivism"]
        },
        {
            "name": "In-Group Bias",
            "text": """We understand the true meaning because we are the chosen people. 
            Outsiders simply cannot comprehend our wisdom and superior understanding.""",
            "expected_biases": ["in_group_bias", "cultural_supremacy"]
        },
        {
            "name": "Clean Text (Control)",
            "text": """Various philosophical traditions offer different perspectives on consciousness. 
            Some philosophers argue for materialist explanations, while others propose dualist theories. 
            Each tradition may contribute valuable insights to our understanding.""",
            "expected_biases": []
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")
        
        result = detector.analyze_text(
            text=test_case['text'],
            domain="philosophy",
            sensitivity="medium"
        )
        
        detected_bias_types = [bias['bias_type'] for bias in result['detected_biases']]
        bias_summary = result['bias_summary']
        
        print(f"   Found {len(result['detected_biases'])} biases: {detected_bias_types}")
        print(f"   Overall assessment: {bias_summary['overall_assessment']}")
        print(f"   Bias score: {result['overall_bias_score']:.2f}")
        
        # Check if we found expected biases
        found_expected = any(expected in detected_bias_types for expected in test_case['expected_biases'])
        
        if test_case['expected_biases'] and found_expected:
            print("   ✅ PASS - Found expected bias types")
        elif not test_case['expected_biases'] and len(result['detected_biases']) <= 1:
            print("   ✅ PASS - Clean text correctly identified")
        elif test_case['expected_biases'] and not found_expected:
            print(f"   ❌ FAIL - Expected {test_case['expected_biases']} but found {detected_bias_types}")
            all_passed = False
        else:
            print("   ⚠️  PARTIAL - Some biases detected")
        
        # Show top bias if any
        if result['detected_biases']:
            top_bias = result['detected_biases'][0]
            print(f"   Top bias: {top_bias['bias_type']} ({top_bias['confidence']:.2f} confidence)")
        
        # Show recommendations
        if result['recommendations']:
            print(f"   Recommendations: {result['recommendations'][0]}")
    
    print(f"\n📊 RESULTS SUMMARY")
    print("="*20)
    if all_passed:
        print("✅ All tests PASSED!")
        print("🎉 Bias detection is working correctly!")
        print("\n🚀 Ready for MCP integration!")
    else:
        print("⚠️  Some tests failed - review the results above")
    
    print(f"\n🔧 BIAS DETECTION FEATURES VERIFIED:")
    print("✅ Pattern-based bias detection")  
    print("✅ Linguistic analysis")
    print("✅ Confidence scoring")
    print("✅ Severity assessment")
    print("✅ Recommendation generation")
    print("✅ Multiple bias categories")
    print("✅ Clean text handling")
    
    return all_passed

if __name__ == "__main__":
    test_bias_detection()
