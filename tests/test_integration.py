"""Integration tests for the Yggdrasil system."""

import pytest
import asyncio
from yggdrasil.database.connection import DatabaseManager
from yggdrasil.agents.mcp_agent_manager import MCPAgentManager
from test_config import get_test_settings, SAMPLE_SPIRITUAL_TEXT, SAMPLE_PHILOSOPHICAL_TEXT, TEST_DATABASE_URL, TEST_QDRANT_URL
from sqlalchemy import text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_system_integration():
    """Test complete system integration."""
    
    # Use test configuration
    test_settings = get_test_settings()
    
    # Test database connection
    db_manager = DatabaseManager()
    await db_manager.initialize_hybrid_system()
    
    try:
        # Test agent initialization
        agent_manager = MCPAgentManager(
            postgres_url=TEST_DATABASE_URL,
            qdrant_url=TEST_QDRANT_URL
        )
        await agent_manager.initialize()
        
        # Test analysis pipeline
        result = await agent_manager.analyze_text(
            text=SAMPLE_SPIRITUAL_TEXT,
            analysis_type="theme_analysis"
        )
        
        assert result.success
        assert result.data is not None
        
        print(" Full system integration test passed")
        
    finally:
        await db_manager.close_connections()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_hybrid_system():
    """Test PostgreSQL + Qdrant hybrid system."""
    
    db_manager = DatabaseManager()
    await db_manager.initialize_hybrid_system()
    
    try:
        # Test PostgreSQL connection
        async with db_manager.get_async_session() as session:
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1
        
        # Test Qdrant connection (if available)
        from yggdrasil.database.qdrant_manager import qdrant_manager
        await qdrant_manager.initialize()
        
        print(" Hybrid database system test passed")
        
    finally:
        await db_manager.close_connections()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_pipeline():
    """Test complete AI agent pipeline."""
    
    agent_manager = MCPAgentManager(
        postgres_url=TEST_DATABASE_URL,
        qdrant_url=TEST_QDRANT_URL
    )
    await agent_manager.initialize()
    
    # Test multiple analysis types
    analysis_types = ["theme_analysis", "doctrine_analysis", "bias_detection"]
    
    for analysis_type in analysis_types:
        result = await agent_manager.analyze_text(
            text=SAMPLE_PHILOSOPHICAL_TEXT,
            analysis_type=analysis_type
        )
        
        assert result.success, f"Failed for analysis type: {analysis_type}"
        assert result.data is not None
        
        print(f" {analysis_type} test passed")


@pytest.mark.integration
@pytest.mark.asyncio 
async def test_configuration_loading():
    """Test configuration loading and validation."""
    
    from yggdrasil.config import settings
    
    # Test that configuration loads properly
    assert settings.postgres_host is not None
    assert settings.postgres_port > 0
    assert settings.qdrant_host is not None
    assert settings.qdrant_port > 0
    
    # Test database URL generation
    db_url = settings.database_url
    assert "postgresql://" in db_url
    assert settings.postgres_host in db_url
    
    # Test Qdrant URL generation
    qdrant_url = settings.qdrant_url
    assert "http://" in qdrant_url
    assert settings.qdrant_host in qdrant_url
    
    print(" Configuration loading test passed")


if __name__ == "__main__":
    asyncio.run(test_full_system_integration())
    asyncio.run(test_database_hybrid_system())
    asyncio.run(test_agent_pipeline())
    asyncio.run(test_configuration_loading())
