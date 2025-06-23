#!/usr/bin/env python3
"""
Smart Storage Agent - AI-powered storage optimization for Yggdrasil
Uses machine learning to make intelligent storage decisions
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib
import spacy
from sentence_transformers import SentenceTransformer

# Database imports
import psycopg2
from sqlalchemy import create_engine, text
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)

class StorageDecision(Enum):
    """Storage decision types"""
    POSTGRES_METADATA_ONLY = "postgres_metadata"
    POSTGRES_FULL = "postgres_full"
    QDRANT_VECTORS = "qdrant_vectors"
    HYBRID_OPTIMAL = "hybrid_optimal"
    DYNAMIC_TABLE = "dynamic_table"

@dataclass
class ContentAnalysis:
    """Comprehensive content analysis"""
    url: str
    title: str
    content_preview: str
    estimated_size: int
    language: str
    domain: str
    content_type: str
    
    # AI-generated features
    semantic_complexity: float
    topic_coherence: float
    information_density: float
    query_potential: float
    
    # Storage recommendation
    storage_decision: StorageDecision
    confidence_score: float
    reasoning: List[str]

class SmartStorageAgent:
    """AI agent for intelligent storage decisions"""
    
    def __init__(self, postgres_url: str, qdrant_url: str):
        self.postgres_url = postgres_url
        self.qdrant_url = qdrant_url
        self.engine = create_engine(postgres_url)
        self.qdrant_client = QdrantClient(url=qdrant_url)
        
        # AI models
        self.sentence_transformer = None
        self.storage_classifier = None
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        
        # Performance tracking
        self.decision_history = []
        self.performance_metrics = {}
        
    async def initialize(self):
        """Initialize AI models"""
        try:
            # Load sentence transformer for embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load spaCy for NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Some features will be limited.")
                self.nlp = None
            
            # Initialize or load storage classifier
            await self._initialize_storage_classifier()
            
            logger.info("Smart Storage Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Smart Storage Agent: {e}")
            raise
    
    async def analyze_content(self, url: str, content: str, metadata: Dict[str, Any]) -> ContentAnalysis:
        """Perform comprehensive content analysis"""
        
        try:
            # Basic content analysis
            title = metadata.get('title', url.split('/')[-1])
            content_preview = content[:1000] if content else ""
            estimated_size = len(content.encode('utf-8')) if content else 0
            
            # AI-powered analysis
            semantic_complexity = await self._analyze_semantic_complexity(content_preview)
            topic_coherence = await self._analyze_topic_coherence(content_preview)
            information_density = await self._analyze_information_density(content_preview)
            query_potential = await self._analyze_query_potential(content_preview, metadata)
            
            # Determine domain and content type
            domain = await self._classify_domain(content_preview, url)
            content_type = await self._classify_content_type(content_preview, url, estimated_size)
            language = await self._detect_language(content_preview)
            
            # Make storage decision
            storage_decision, confidence, reasoning = await self._make_storage_decision(
                content_preview, estimated_size, semantic_complexity, 
                topic_coherence, information_density, query_potential,
                domain, content_type
            )
            
            analysis = ContentAnalysis(
                url=url,
                title=title,
                content_preview=content_preview,
                estimated_size=estimated_size,
                language=language,
                domain=domain,
                content_type=content_type,
                semantic_complexity=semantic_complexity,
                topic_coherence=topic_coherence,
                information_density=information_density,
                query_potential=query_potential,
                storage_decision=storage_decision,
                confidence_score=confidence,
                reasoning=reasoning
            )
            
            # Track decision for learning
            self.decision_history.append({
                'timestamp': datetime.utcnow(),
                'analysis': analysis,
                'features': [semantic_complexity, topic_coherence, information_density, query_potential]
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            # Return default analysis
            return ContentAnalysis(
                url=url,
                title=url.split('/')[-1],
                content_preview=content[:500],
                estimated_size=len(content.encode('utf-8')),
                language="en",
                domain="general",
                content_type="text",
                semantic_complexity=0.5,
                topic_coherence=0.5,
                information_density=0.5,
                query_potential=0.5,
                storage_decision=StorageDecision.HYBRID_OPTIMAL,
                confidence_score=0.3,
                reasoning=["Default analysis due to error"]
            )
    
    async def _analyze_semantic_complexity(self, content: str) -> float:
        """Analyze semantic complexity of content"""
        
        if not content or not self.nlp:
            return 0.5  # Default medium complexity
        
        try:
            doc = self.nlp(content[:500])  # Analyze first 500 chars
            
            # Complexity factors
            avg_word_length = np.mean([len(token.text) for token in doc if token.is_alpha])
            syntactic_complexity = len([token for token in doc if token.dep_ in ['compound', 'conj', 'prep']])
            entity_density = len(doc.ents) / len(doc) if len(doc) > 0 else 0
            
            # Normalize to 0-1 scale
            complexity = min(1.0, (avg_word_length * 0.1) + (syntactic_complexity * 0.01) + entity_density)
            
            return complexity
            
        except Exception as e:
            logger.error(f"Error analyzing semantic complexity: {e}")
            return 0.5
    
    async def _analyze_topic_coherence(self, content: str) -> float:
        """Analyze topic coherence of content"""
        
        if not content:
            return 0.5
        
        try:
            # Simple coherence analysis based on word repetition and structure
            words = content.lower().split()
            if len(words) < 10:
                return 0.3  # Too short for coherence analysis
            
            # Calculate word frequency distribution
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Coherence based on repetition patterns
            if not word_freq:
                return 0.3
            
            freq_values = list(word_freq.values())
            coherence = min(1.0, np.std(freq_values) / np.mean(freq_values)) if np.mean(freq_values) > 0 else 0.5
            
            return coherence
            
        except Exception as e:
            logger.error(f"Error analyzing topic coherence: {e}")
            return 0.5
    
    async def _analyze_information_density(self, content: str) -> float:
        """Analyze information density of content"""
        
        if not content:
            return 0.3
        
        try:
            # Information density metrics
            sentences = content.split('.')
            words = content.split()
            
            if not sentences or not words:
                return 0.3
            
            # Metrics
            avg_sentence_length = len(words) / len(sentences)
            unique_word_ratio = len(set(words)) / len(words) if words else 0
            punctuation_density = sum(1 for char in content if char in '.,;:!?') / len(content)
            
            # Normalize and combine
            density = min(1.0, (avg_sentence_length * 0.02) + unique_word_ratio + (punctuation_density * 2))
            
            return density
            
        except Exception as e:
            logger.error(f"Error analyzing information density: {e}")
            return 0.5
    
    async def _analyze_query_potential(self, content: str, metadata: Dict[str, Any]) -> float:
        """Analyze potential for future queries"""
        
        try:
            # Query potential factors
            content_length = len(content)
            has_structured_data = any(marker in content.lower() for marker in ['chapter', 'section', 'table', 'list'])
            has_references = any(marker in content.lower() for marker in ['http', 'www', 'doi', 'isbn'])
            domain_value = 1.0 if metadata.get('domain') in ['science', 'philosophy', 'literature'] else 0.5
            
            # Combine factors
            length_factor = min(1.0, content_length / 10000)  # Longer content = higher query potential
            structure_factor = 1.0 if has_structured_data else 0.3
            reference_factor = 1.0 if has_references else 0.5
            
            query_potential = (length_factor + structure_factor + reference_factor + domain_value) / 4
            
            return min(1.0, query_potential)
            
        except Exception as e:
            logger.error(f"Error analyzing query potential: {e}")
            return 0.6
    
    async def _classify_domain(self, content: str, url: str) -> str:
        """Classify content domain using AI"""
        
        domain_keywords = {
            "religion": ["god", "spiritual", "faith", "prayer", "divine", "sacred", "bible", "quran"],
            "philosophy": ["philosophy", "ethics", "metaphysics", "logic", "consciousness", "existence"],
            "science": ["research", "study", "analysis", "hypothesis", "experiment", "data", "theory"],
            "literature": ["novel", "story", "character", "plot", "literary", "fiction", "poetry"],
            "history": ["historical", "ancient", "medieval", "century", "civilization", "culture"],
            "technology": ["technology", "software", "computer", "digital", "programming", "algorithm"],
            "medicine": ["medical", "health", "treatment", "patient", "clinical", "disease", "therapy"],
            "mathematics": ["mathematics", "equation", "theorem", "proof", "number", "formula", "calculation"]
        }
        
        content_lower = content.lower()
        url_lower = url.lower()
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower or keyword in url_lower)
            domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if domain_scores else "general"
    
    async def _classify_content_type(self, content: str, url: str, size: int) -> str:
        """Classify content type"""
        
        # URL-based classification
        if any(indicator in url.lower() for indicator in ['book', 'ebook', 'gutenberg']):
            return "book"
        if any(indicator in url.lower() for indicator in ['paper', 'journal', 'arxiv']):
            return "academic_paper"
        if any(indicator in url.lower() for indicator in ['wiki', 'encyclopedia']):
            return "reference"
        
        # Size-based classification
        if size > 10_000_000:  # > 10MB
            return "book"
        elif size > 1_000_000:  # > 1MB
            return "large_document"
        elif size > 100_000:  # > 100KB
            return "medium_document"
        else:
            return "small_document"
    
    async def _detect_language(self, content: str) -> str:
        """Detect content language"""
        # Simplified language detection
        # In production, use langdetect or similar
        return "en"
    
    async def _make_storage_decision(self, content: str, size: int, semantic_complexity: float,
                                   topic_coherence: float, information_density: float, 
                                   query_potential: float, domain: str, content_type: str) -> Tuple[StorageDecision, float, List[str]]:
        """Make intelligent storage decision"""
        
        reasoning = []
        
        # Decision logic based on multiple factors
        if size < 50_000:  # < 50KB
            decision = StorageDecision.POSTGRES_FULL
            confidence = 0.9
            reasoning.append("Small size suitable for PostgreSQL full storage")
            
        elif size > 50_000_000:  # > 50MB
            decision = StorageDecision.QDRANT_VECTORS
            confidence = 0.95
            reasoning.append("Large size requires vector storage in Qdrant")
            
        elif query_potential > 0.8 and semantic_complexity > 0.7:
            decision = StorageDecision.HYBRID_OPTIMAL
            confidence = 0.85
            reasoning.append("High query potential and complexity benefit from hybrid storage")
            
        elif information_density > 0.8:
            decision = StorageDecision.DYNAMIC_TABLE
            confidence = 0.8
            reasoning.append("High information density warrants dedicated table")
            
        elif domain in ["science", "philosophy", "literature"] and size > 1_000_000:
            decision = StorageDecision.HYBRID_OPTIMAL
            confidence = 0.75
            reasoning.append("Academic domain with substantial content benefits from hybrid approach")
            
        else:
            decision = StorageDecision.POSTGRES_METADATA_ONLY
            confidence = 0.6
            reasoning.append("Default to PostgreSQL metadata with content links")
        
        # Use ML classifier if available
        if self.storage_classifier:
            try:
                features = np.array([[size, semantic_complexity, topic_coherence, 
                                    information_density, query_potential]])
                ml_prediction = self.storage_classifier.predict(features)[0]
                ml_confidence = max(self.storage_classifier.predict_proba(features)[0])
                
                if ml_confidence > confidence:
                    # Trust ML prediction if more confident
                    decision = StorageDecision(ml_prediction)
                    confidence = ml_confidence
                    reasoning.append(f"ML classifier prediction with {ml_confidence:.2f} confidence")
                    
            except Exception as e:
                logger.error(f"Error using ML classifier: {e}")
        
        return decision, confidence, reasoning
    
    async def _initialize_storage_classifier(self):
        """Initialize or load the storage classification model"""
        
        model_path = "/Users/grant/Desktop/Solomon/Database/S.IO/models/storage_classifier.joblib"
        
        try:
            # Try to load existing model
            self.storage_classifier = joblib.load(model_path)
            logger.info("Loaded existing storage classifier")
        
        except (FileNotFoundError, Exception):
            # Train new model with synthetic data
            logger.info("Training new storage classifier")
            await self._train_storage_classifier(model_path)
    
    async def _train_storage_classifier(self, model_path: str):
        """Train storage classification model with synthetic data"""
        
        try:
            # Generate synthetic training data
            # In production, this would use historical decisions
            X, y = self._generate_training_data()
            
            # Train classifier
            self.storage_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.storage_classifier.fit(X, y)
            
            # Save model
            import os
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self.storage_classifier, model_path)
            
            logger.info("Storage classifier trained and saved")
            
        except Exception as e:
            logger.error(f"Error training storage classifier: {e}")
            self.storage_classifier = None
    
    def _generate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for storage classifier"""
        
        # Synthetic data based on storage decision rules
        data = []
        labels = []
        
        # Small documents -> POSTGRES_FULL
        for _ in range(100):
            size = np.random.randint(1000, 50000)
            complexity = np.random.uniform(0.1, 0.6)
            coherence = np.random.uniform(0.3, 0.8)
            density = np.random.uniform(0.2, 0.7)
            query_potential = np.random.uniform(0.2, 0.6)
            
            data.append([size, complexity, coherence, density, query_potential])
            labels.append("postgres_full")
        
        # Large documents -> QDRANT_VECTORS
        for _ in range(100):
            size = np.random.randint(50000000, 100000000)
            complexity = np.random.uniform(0.4, 0.9)
            coherence = np.random.uniform(0.5, 0.9)
            density = np.random.uniform(0.6, 0.9)
            query_potential = np.random.uniform(0.7, 1.0)
            
            data.append([size, complexity, coherence, density, query_potential])
            labels.append("qdrant_vectors")
        
        # Medium complex documents -> HYBRID_OPTIMAL
        for _ in range(100):
            size = np.random.randint(100000, 10000000)
            complexity = np.random.uniform(0.6, 0.9)
            coherence = np.random.uniform(0.6, 0.9)
            density = np.random.uniform(0.7, 0.9)
            query_potential = np.random.uniform(0.7, 0.9)
            
            data.append([size, complexity, coherence, density, query_potential])
            labels.append("hybrid_optimal")
        
        return np.array(data), np.array(labels)
    
    async def optimize_storage_performance(self) -> Dict[str, Any]:
        """Optimize storage performance based on usage patterns"""
        
        try:
            # Analyze recent decisions
            recent_decisions = self.decision_history[-100:] if len(self.decision_history) > 100 else self.decision_history
            
            # Performance analysis
            decision_distribution = {}
            avg_confidence = 0
            
            for entry in recent_decisions:
                decision = entry['analysis'].storage_decision.value
                decision_distribution[decision] = decision_distribution.get(decision, 0) + 1
                avg_confidence += entry['analysis'].confidence_score
            
            if recent_decisions:
                avg_confidence /= len(recent_decisions)
            
            # Generate recommendations
            recommendations = []
            
            if avg_confidence < 0.7:
                recommendations.append("Consider retraining the storage classifier with more data")
            
            if decision_distribution.get("hybrid_optimal", 0) > len(recent_decisions) * 0.5:
                recommendations.append("High hybrid usage - consider optimizing PostgreSQL-Qdrant sync")
            
            if decision_distribution.get("dynamic_table", 0) > 20:
                recommendations.append("Many dynamic tables created - consider table consolidation")
            
            return {
                "status": "analysis_complete",
                "total_decisions": len(self.decision_history),
                "recent_decisions": len(recent_decisions),
                "decision_distribution": decision_distribution,
                "average_confidence": avg_confidence,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing storage performance: {e}")
            return {"status": "error", "message": str(e)}
