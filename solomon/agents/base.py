"""Enhanced base agent class for Solomon project with RAG and hybrid database integration."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import time

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFacePipeline
from pydantic import BaseModel, Field
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from solomon.config import settings
from solomon.database.connection import db_manager, get_qdrant
from solomon.database.qdrant_manager import qdrant_manager
from solomon.database.models import SpiritualText, FieldCategory, SubfieldCategory


logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Standard result format for agent operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[Dict[str, Any]] = Field(default_factory=list)  # For RAG citations


class BaseAgent(ABC):
    """Enhanced base class for all Solomon agents with RAG and hybrid database integration."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_model: Optional[str] = None,
        use_huggingface: bool = True,
        enable_rag: bool = True,
        max_context_length: int = 4000,
    ):
        self.name = name
        self.description = description
        self.use_huggingface = use_huggingface
        self.enable_rag = enable_rag
        self.max_context_length = max_context_length
        
        # Initialize LLM
        if use_huggingface:
            # Use Hugging Face local models
            model_name = llm_model or settings.hf_model_name
            self.llm = HuggingFacePipeline.from_model_id(
                model_id=model_name,
                task="text-generation",
                model_kwargs={
                    "temperature": 0.7,
                    "max_length": max_context_length,
                    "do_sample": True,
                },
                pipeline_kwargs={"max_new_tokens": 512}
            )
        else:
            # Use Ollama as fallback
            self.llm = Ollama(
                model=settings.ollama_model,
                base_url=settings.ollama_host,
                temperature=0.7,
            )
        
        # Database connections
        self.db_manager = db_manager
        self.qdrant_manager = qdrant_manager
        
        # Performance tracking
        self.execution_stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'total_execution_time': 0.0,
            'avg_execution_time': 0.0
        }
        
        logger.info(f"Initialized {self.name} agent with enhanced capabilities")
    
    async def initialize(self):
        """Initialize the agent's database connections."""
        try:
            if not self.qdrant_manager.client:
                await self.qdrant_manager.initialize()
            logger.info(f"{self.name} agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} agent: {e}")
            raise
    
    @abstractmethod
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Process a query using agent-specific logic."""
        pass
    
    async def hybrid_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search across PostgreSQL and Qdrant."""
        try:
            # Vector search in Qdrant
            vector_results = await self.qdrant_manager.search_similar(
                query=query,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filters
            )
            
            # Enrich with PostgreSQL metadata
            enriched_results = []
            async with self.db_manager.get_async_session() as session:
                for result in vector_results:
                    text_id = result['id']
                    
                    # Get full text data from PostgreSQL
                    from sqlalchemy import select
                    db_result = await session.execute(
                        select(SpiritualText).where(SpiritualText.qdrant_point_id == text_id)
                    )
                    spiritual_text = db_result.scalar_one_or_none()
                    
                    if spiritual_text:
                        enriched_result = {
                            'id': spiritual_text.id,
                            'title': spiritual_text.title,
                            'content': spiritual_text.content,
                            'text_type': spiritual_text.text_type.value,
                            'language': spiritual_text.language.value,
                            'book': spiritual_text.book,
                            'chapter': spiritual_text.chapter,
                            'verse': spiritual_text.verse,
                            'author': spiritual_text.author,
                            'source_url': spiritual_text.source_url,
                            'similarity_score': result['score'],
                            'qdrant_payload': result['payload']
                        }
                        enriched_results.append(enriched_result)
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    async def get_context_texts(
        self, 
        query: str, 
        text_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get relevant context texts for RAG using hybrid search."""
        filters = {}
        if text_types:
            filters['text_type'] = text_types[0] if len(text_types) == 1 else text_types
        
        return await self.hybrid_search(query, filters=filters, limit=limit)
    
    async def generate_rag_response(
        self, 
        query: str, 
        context_texts: List[Dict[str, Any]],
        system_prompt: str = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate response using RAG with context texts."""
        if not context_texts:
            # Fallback to basic generation without context
            return await self._generate_basic_response(query, system_prompt), []
        
        # Prepare context
        context_content = "\n\n".join([
            f"Source: {text['title']} ({text.get('book', 'Unknown')})\nContent: {text['content'][:500]}..."
            for text in context_texts[:3]  # Limit to top 3 for context length
        ])
        
        # Create RAG prompt
        if system_prompt:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""Based on the following context from spiritual texts, please answer the question.

Context:
{context_content}

Question: {query}

Please provide a comprehensive answer based on the context provided, and mention which sources you're drawing from.""")
            ]
        else:
            prompt = f"""Based on the following context from spiritual texts, please answer the question.

Context:
{context_content}

Question: {query}

Answer:"""
            
        try:
            if hasattr(self.llm, 'invoke'):
                if system_prompt:
                    response = await self.llm.ainvoke(messages)
                else:
                    response = await self.llm.ainvoke(prompt)
            else:
                response = self.llm(prompt)
            
            # Extract citations
            citations = [
                {
                    'title': text['title'],
                    'source': text.get('source_url', ''),
                    'text_type': text['text_type'],
                    'similarity_score': text.get('similarity_score', 0.0)
                }
                for text in context_texts
            ]
            
            return response, citations
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return f"Error generating response: {str(e)}", []
    
    async def _generate_basic_response(self, query: str, system_prompt: str = None) -> str:
        """Generate basic response without RAG context."""
        try:
            if system_prompt:
                prompt = f"{system_prompt}\n\nQuery: {query}\n\nResponse:"
            else:
                prompt = f"Query: {query}\n\nResponse:"
            
            if hasattr(self.llm, 'invoke'):
                response = await self.llm.ainvoke(prompt)
            else:
                response = self.llm(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating basic response: {e}")
            return f"Error generating response: {str(e)}"
    
    async def query_database(
        self, 
        query_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query PostgreSQL database directly for structured data."""
        try:
            async with self.db_manager.get_async_session() as session:
                from sqlalchemy import select, func
                
                if query_type == "text_counts":
                    # Get text counts by type
                    result = await session.execute(
                        select(SpiritualText.text_type, func.count(SpiritualText.id))
                        .group_by(SpiritualText.text_type)
                    )
                    return [{"text_type": row[0].value, "count": row[1]} for row in result]
                
                elif query_type == "recent_texts":
                    # Get recent texts
                    from datetime import timedelta
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    result = await session.execute(
                        select(SpiritualText)
                        .where(SpiritualText.created_at >= yesterday)
                        .limit(10)
                    )
                    texts = result.scalars().all()
                    return [
                        {
                            "id": str(text.id),
                            "title": text.title,
                            "text_type": text.text_type.value,
                            "created_at": text.created_at.isoformat()
                        }
                        for text in texts
                    ]
                
                elif query_type == "field_categories":
                    # Get field categories
                    result = await session.execute(select(FieldCategory))
                    categories = result.scalars().all()
                    return [
                        {
                            "id": str(cat.id),
                            "field_name": cat.field_name,
                            "description": cat.description
                        }
                        for cat in categories
                    ]
                
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return []
    
    def update_stats(self, execution_time: float, success: bool):
        """Update agent performance statistics."""
        self.execution_stats['total_queries'] += 1
        if success:
            self.execution_stats['successful_queries'] += 1
        
        self.execution_stats['total_execution_time'] += execution_time
        self.execution_stats['avg_execution_time'] = (
            self.execution_stats['total_execution_time'] / self.execution_stats['total_queries']
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        success_rate = 0.0
        if self.execution_stats['total_queries'] > 0:
            success_rate = (
                self.execution_stats['successful_queries'] / 
                self.execution_stats['total_queries']
            ) * 100
        
        return {
            'agent_name': self.name,
            'total_queries': self.execution_stats['total_queries'],
            'successful_queries': self.execution_stats['successful_queries'],
            'success_rate': f"{success_rate:.2f}%",
            'avg_execution_time': f"{self.execution_stats['avg_execution_time']:.3f}s"
        }
    
    async def execute_with_timing(self, coro):
        """Execute coroutine with timing measurement."""
        start_time = time.time()
        try:
            result = await coro
            execution_time = time.time() - start_time
            self.update_stats(execution_time, True)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_stats(execution_time, False)
            raise
