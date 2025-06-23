"""Qdrant vector database manager for Solomon project."""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from yggdrasil.config import settings


logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant vector database connections and operations."""
    
    def __init__(self):
        self.client = None
        self.embedding_model = None
        self.collection_name = settings.qdrant_collection_name
        self.embedding_dimension = settings.embedding_dimension
        
    async def initialize(self):
        """Initialize Qdrant client and embedding model."""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                timeout=60
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(
                settings.hf_embedding_model,
                cache_folder=settings.hf_cache_dir
            )
            
            # Create collection if it doesn't exist
            await self._create_collection_if_not_exists()
            
            logger.info(f"Qdrant manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant manager: {e}")
            raise
    
    async def _create_collection_if_not_exists(self):
        """Create the spiritual texts collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a given text."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embeddings = self.embedding_model.encode(
                texts, 
                convert_to_tensor=False,
                batch_size=settings.embedding_batch_size if hasattr(settings, 'embedding_batch_size') else 32
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def add_text(
        self, 
        text_id: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a single text to Qdrant."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Generate embedding
            embedding = self.generate_embedding(content)
            
            # Create point
            point = PointStruct(
                id=text_id,
                vector=embedding,
                payload=metadata or {}
            )
            
            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Added text to Qdrant: {text_id}")
            return text_id
            
        except Exception as e:
            logger.error(f"Failed to add text to Qdrant: {e}")
            raise
    
    async def add_texts_batch(
        self, 
        texts: List[Tuple[str, str, Dict[str, Any]]]
    ) -> List[str]:
        """Add multiple texts to Qdrant in batch."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Extract content for batch embedding generation
            contents = [text[1] for text in texts]
            embeddings = self.generate_embeddings_batch(contents)
            
            # Create points
            points = []
            for i, (text_id, content, metadata) in enumerate(texts):
                point = PointStruct(
                    id=text_id,
                    vector=embeddings[i],
                    payload=metadata or {}
                )
                points.append(point)
            
            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            text_ids = [text[0] for text in texts]
            logger.info(f"Added {len(text_ids)} texts to Qdrant")
            return text_ids
            
        except Exception as e:
            logger.error(f"Failed to add texts batch to Qdrant: {e}")
            raise
    
    async def search_similar(
        self, 
        query: str, 
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar texts in Qdrant."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )
            
            # Search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            logger.debug(f"Found {len(results)} similar texts for query")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar texts: {e}")
            raise
    
    async def delete_text(self, text_id: str) -> bool:
        """Delete a text from Qdrant."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[text_id]
                )
            )
            
            logger.debug(f"Deleted text from Qdrant: {text_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete text from Qdrant: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.config.name,
                'status': info.status,
                'vectors_count': info.vectors_count,
                'indexed_vectors_count': info.indexed_vectors_count,
                'points_count': info.points_count
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise
    
    async def close(self):
        """Close Qdrant client connection."""
        if self.client:
            self.client.close()
            logger.info("Qdrant client connection closed")


# Global Qdrant manager instance
qdrant_manager = QdrantManager()


@asynccontextmanager
async def get_qdrant_manager():
    """Context manager for Qdrant operations."""
    if not qdrant_manager.client:
        await qdrant_manager.initialize()
    
    try:
        yield qdrant_manager
    finally:
        # Keep connection open for reuse
        pass
