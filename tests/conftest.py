"""Pytest configuration and fixtures for Yggdrasil tests."""

import pytest
import asyncio
import os
from yggdrasil.database.connection import DatabaseManager
from yggdrasil.config import settings
from yggdrasil.utils.logging import setup_logging


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Setup logging for tests."""
    # Set debug mode for tests
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    logger = setup_logging()
    logger.info("Test session starting with debug logging enabled")
    
    yield logger
    
    logger.info("Test session completed")


@pytest.fixture(scope="session")
async def db_manager():
    """Create test database manager."""
    # Override settings for testing
    original_db = settings.postgres_db
    settings.postgres_db = "yggdrasil_test"
    
    db_manager = DatabaseManager()
    
    try:
        await db_manager.initialize_hybrid_system()
        yield db_manager
    finally:
        await db_manager.close_connections()
        # Restore original database name
        settings.postgres_db = original_db


@pytest.fixture
async def async_session(db_manager):
    """Provide an async database session for tests."""
    async with db_manager.get_async_session() as session:
        yield session


@pytest.fixture
def sync_session(db_manager):
    """Provide a sync database session for tests."""
    session = db_manager.get_sync_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
async def test_settings():
    """Provide test settings configuration."""
    from test_config import get_test_settings
    return get_test_settings()


# Test data fixtures
@pytest.fixture
def sample_spiritual_text():
    """Sample spiritual text for testing."""
    from test_config import SAMPLE_SPIRITUAL_TEXT
    return SAMPLE_SPIRITUAL_TEXT


@pytest.fixture
def sample_philosophical_text():
    """Sample philosophical text for testing."""
    from test_config import SAMPLE_PHILOSOPHICAL_TEXT
    return SAMPLE_PHILOSOPHICAL_TEXT


@pytest.fixture
def biased_text_sample():
    """Biased text sample for testing."""
    from test_config import BIASED_TEXT_SAMPLE
    return BIASED_TEXT_SAMPLE
