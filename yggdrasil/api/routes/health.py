"""Health check API routes."""

from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from yggdrasil.config import settings
from yggdrasil.agents.orchestrator import AgentOrchestrator
from yggdrasil.database import db_manager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    agents: Dict[str, bool]
    database: bool
    configuration: Dict[str, Any]


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator dependency."""
    from yggdrasil.api.main import orchestrator
    return orchestrator


@router.get("/", response_model=HealthResponse)
async def health_check(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Comprehensive health check."""
    
    # Check agent health
    agent_health = {}
    if orchestrator:
        try:
            agent_health = await orchestrator.health_check()
        except Exception as e:
            agent_health = {"error": str(e)}
    
    # Check database health
    database_healthy = True
    try:
        from yggdrasil.database import db_manager
        # Simple database connection test could be added here
    except Exception:
        database_healthy = False
    
    # Overall status
    all_agents_healthy = all(agent_health.values()) if agent_health else False
    overall_status = "healthy" if all_agents_healthy and database_healthy else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version="0.1.0",
        agents=agent_health,
        database=database_healthy,
        configuration={
            "debug": settings.debug,
            "log_level": settings.log_level,
            "openai_configured": bool(settings.openai_api_key),
            "ollama_host": settings.ollama_host,
            "embedding_model": settings.embedding_model,
        }
    )


@router.get("/agents")
async def agent_health(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Check individual agent health."""
    if not orchestrator:
        return {"error": "Orchestrator not available"}
    
    try:
        agent_status = await orchestrator.health_check()
        return {
            "agents": agent_status,
            "total_agents": len(agent_status),
            "healthy_agents": sum(1 for status in agent_status.values() if status),
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/database")
async def database_health():
    """Check database health."""
    try:
        from yggdrasil.database import db_manager
        
        # Test database connection
        async with db_manager.get_async_session() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            result.fetchone()
        
        return {
            "status": "healthy",
            "database_url": settings.database_url.split("@")[-1],  # Hide credentials
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.get("/config")
async def configuration_info():
    """Get configuration information."""
    return {
        "app_name": settings.app_name,
        "version": "0.1.0",
        "debug": settings.debug,
        "log_level": settings.log_level,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "openai_configured": bool(settings.openai_api_key),
        "openai_model": settings.openai_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "ollama_host": settings.ollama_host,
        "ollama_model": settings.ollama_model,
        "qdrant_host": settings.qdrant_host,
        "qdrant_port": settings.qdrant_port,
        "max_concurrent_requests": settings.max_concurrent_requests,
        "timestamp": datetime.now()
    }
