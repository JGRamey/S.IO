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
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Database connection details - use environment variables
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5431, env="POSTGRES_PORT")  # Updated to use 5431 as default
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="yggdrasil", env="POSTGRES_DB")
    
    @property
    def database_url(self) -> str:
        """Generate database URL from individual components."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Vector Database
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_collection_name: str = "spiritual_texts"
    
    @property
    def qdrant_url(self) -> str:
        """Generate Qdrant URL from individual components."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
    
    # Hugging Face Models
    hf_model_name: str = Field(default="microsoft/DialoGPT-large", env="HF_MODEL_NAME")  # Local LLM model
    hf_embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="HF_EMBEDDING_MODEL")  # Local embedding model
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")  # Dimension for all-MiniLM-L6-v2
    hf_cache_dir: Optional[str] = Field(default=None, env="HF_CACHE_DIR")  # Uses default HF cache
    use_local_models_only: bool = Field(default=True, env="USE_LOCAL_MODELS_ONLY")  # Force local models only
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    
    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    rag_top_k: int = Field(default=5, env="RAG_TOP_K")
    
    # Performance
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
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
