"""Database connection management."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from solomon.config import settings
from .models import Base


class DatabaseManager:
    """Manages database connections and sessions."""
    
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
        """Create all tables (for development/testing)."""
        Base.metadata.create_all(bind=self.sync_engine)
    
    def drop_tables(self):
        """Drop all tables (for development/testing)."""
        Base.metadata.drop_all(bind=self.sync_engine)
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    def get_sync_session(self) -> Session:
        """Get a sync database session."""
        session = self.sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def close(self):
        """Close database connections."""
        await self.async_engine.dispose()
        self.sync_engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with db_manager.get_async_session() as session:
        yield session
