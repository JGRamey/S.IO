"""Database connection management."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from yggdrasil.config import settings
from .models import Base
from .qdrant_manager import qdrant_manager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions for hybrid PostgreSQL + Qdrant architecture."""
    
    def __init__(self):
        # Sync engine for migrations
        self.sync_engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Async engine for application
        async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.async_engine = create_async_engine(
            async_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Session factories
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            autocommit=False,
            autoflush=False,
        )
        
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.sync_engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.sync_engine)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
    async def initialize_hybrid_system(self):
        """Initialize both PostgreSQL and Qdrant systems."""
        try:
            # Initialize Qdrant
            await qdrant_manager.initialize()
            
            # Test PostgreSQL connection
            async with self.async_session_factory() as session:
                await session.execute("SELECT 1")
            
            logger.info("Hybrid database system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize hybrid database system: {e}")
            raise
    
    @asynccontextmanager
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get sync database session."""
        return self.sync_session_factory()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
    async def close_connections(self):
        """Close all database connections."""
        await self.async_engine.dispose()
        self.sync_engine.dispose()
        await qdrant_manager.close()


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI to get database session
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with db_manager.get_async_session() as session:
        yield session


# Dependency for getting Qdrant manager
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
async def get_qdrant():
    """Dependency for getting Qdrant manager."""
    if not qdrant_manager.client:
        await qdrant_manager.initialize()
    return qdrant_manager
