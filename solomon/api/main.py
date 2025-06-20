"""FastAPI application for Solomon project."""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from solomon.config import settings
from solomon.database import get_db_session, DatabaseManager
from solomon.agents.orchestrator import AgentOrchestrator, OrchestrationRequest, AnalysisType
from .routes import analysis, texts, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: AgentOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global orchestrator
    
    # Startup
    logger.info("Starting Solomon API...")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Health check agents
    health_status = await orchestrator.health_check()
    logger.info(f"Agent health status: {health_status}")
    
    # Store orchestrator in app state
    app.state.orchestrator = orchestrator
    
    logger.info("Solomon API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Solomon API...")
    
    if orchestrator:
        await orchestrator.close()
    
    logger.info("Solomon API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Solomon-Sophia API",
    description="AI-powered analysis of spiritual and religious texts",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(texts.router, prefix="/texts", tags=["texts"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Solomon-Sophia API",
        "description": "AI-powered analysis of spiritual and religious texts",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def get_orchestrator() -> AgentOrchestrator:
    """Dependency to get orchestrator instance."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    return orchestrator


# Add orchestrator dependency to app
app.dependency_overrides[AgentOrchestrator] = get_orchestrator


def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "solomon.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()
