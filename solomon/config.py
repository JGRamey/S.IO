"""Configuration management for Solomon project."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Solomon-Sophia"
    debug: bool = False
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Database
    database_url: str = Field(
        default="postgresql://solomon:solomon@localhost:5432/solomon_db",
        description="PostgreSQL database URL"
    )
    
    # Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "spiritual_texts"
    
    # Hugging Face Models
    hf_model_name: str = "microsoft/DialoGPT-large"  # Local LLM model
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Local embedding model
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    hf_cache_dir: Optional[str] = None  # Uses default HF cache
    use_local_models_only: bool = True  # Force local models only
    
    # TensorFlow (optional for advanced models)
    use_tensorflow: bool = False
    tf_model_name: str = "google/flan-t5-base"
    
    # Ollama (local LLM fallback)
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    use_ollama: bool = True  # Enable Ollama as primary LLM
    
    # Scraping
    max_concurrent_requests: int = 5
    request_delay: float = 1.0
    max_retries: int = 3
    
    # Agents
    max_agent_iterations: int = 10
    agent_timeout: int = 300
    
    # Paths
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    cache_dir: Path = Field(default_factory=lambda: Path("cache"))
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        for dir_path in [self.data_dir, self.cache_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
