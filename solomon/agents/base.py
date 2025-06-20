"""Base agent class for Solomon project."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFacePipeline
from pydantic import BaseModel, Field
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from solomon.config import settings


logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Standard result format for agent operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Base class for all Solomon agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_model: Optional[str] = None,
        use_huggingface: bool = True,
    ):
        self.name = name
        self.description = description
        self.use_huggingface = use_huggingface
        
        # Initialize LLM
        if use_huggingface:
            # Use Hugging Face local models
            model_name = llm_model or settings.hf_model_name
            self.llm = HuggingFacePipeline.from_model_id(
                model_id=model_name,
                task="text-generation",
                device=0 if torch.cuda.is_available() else -1,
                model_kwargs={"temperature": 0.1, "max_length": 1000}
            )
        else:
            # Fallback to Ollama (local LLM)
            self.llm = Ollama(
                model=llm_model or settings.ollama_model,
                base_url=settings.ollama_host,
            )
        
        self.logger = logging.getLogger(f"solomon.agents.{name}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main functionality."""
        pass
    
    async def _call_llm(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> str:
        """Call the LLM with error handling."""
        try:
            if hasattr(self.llm, 'ainvoke'):
                response = await self.llm.ainvoke(messages, **kwargs)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                # Sync fallback
                response = self.llm.invoke(messages, **kwargs)
                return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    async def _analyze_text(
        self,
        text: str,
        analysis_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Analyze text with custom prompts."""
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=f"{analysis_prompt}\n\nText to analyze:\n{text}"))
        
        return await self._call_llm(messages)
    
    def _create_result(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **metadata
    ) -> AgentResult:
        """Create a standardized agent result."""
        return AgentResult(
            success=success,
            data=data,
            error=error,
            metadata=metadata
        )
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy and can communicate with its LLM."""
        try:
            test_message = [HumanMessage(content="Hello, respond with 'OK'")]
            response = await self._call_llm(test_message)
            return "ok" in response.lower()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
