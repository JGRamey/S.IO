"""Standardized logging configuration for Yggdrasil project."""

import logging
import sys
from pathlib import Path
from yggdrasil.config import settings


def setup_logging():
    """Configure standardized logging across the application."""
    
    # Create logs directory
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        handlers=[
            logging.FileHandler(settings.logs_dir / "yggdrasil.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Yggdrasil logging system initialized")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
