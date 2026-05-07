"""
FundTrace AI - FastAPI Backend
Main application entry point with ML worker integration
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import graph, stream
from .core.config import get_settings
from .db.neo4j_client import get_driver, close_driver


# Background task references
_worker_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize Neo4j, start ML worker tasks
    - Shutdown: Close Neo4j driver, cancel background tasks
    """
    settings = get_settings()
    
    # Startup
    print("\n" + "="*60)
    print("FUNDTRACE AI - STARTING UP")
    print("="*60)
    
    # Initialize Neo4j driver
    try:
        driver = get_driver()
        app.state.neo4j_driver = driver
        print("✓ Neo4j driver initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Neo4j: {str(e)}")
        raise
    
    # Start ML worker background tasks
    try:
        from .worker import ml_worker
        
        # Start alert broadcaster
        broadcaster_task = asyncio.create_task(stream.alert_broadcaster())
        _worker_tasks.append(broadcaster_task)
        print("✓ Alert broadcaster started")
        
        # Start transaction scoring worker
        worker_task = asyncio.create_task(
            ml_worker.run_worker(driver, stream.alert_queue)
        )
        _worker_tasks.append(worker_task)
        print("✓ Transaction scoring worker started")
        
        # Start PaySim alert streamer
        paysim_task = asyncio.create_task(
            ml_worker.stream_paysim_alerts(stream.alert_queue)
        )
        _worker_tasks.append(paysim_task)
        print("✓ PaySim alert streamer started")
        
    except Exception as e:
        print(f"⚠ Warning: ML worker tasks not started: {str(e)}")
        print("  (This is expected if model hasn't been trained yet)")
    
    print("\n✅ Application startup complete")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print("FUNDTRACE AI - SHUTTING DOWN")
    print("="*60)
    
    # Cancel background tasks
    for task in _worker_tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    print("✓ Background tasks cancelled")
    
    # Close Neo4j driver
    close_driver()
    print("✓ Neo4j driver closed")
    
    print("\n✅ Application shutdown complete")
    print("="*60 + "\n")


# Create FastAPI app
app = FastAPI(
    title="FundTrace AI API",
    version="1.0.0",
    description="Real-time fraud detection and transaction network analysis",
    lifespan=lifespan
)


# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(graph.router)
app.include_router(stream.router)


# Health check endpoint (no auth required)
@app.get("/", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns service status without requiring authentication.
    """
    return {
        "status": "ok",
        "service": "FundTrace AI"
    }


@app.get("/health", tags=["health"])
async def health_check_legacy() -> dict:
    """Legacy health check endpoint."""
    return {"status": "ok"}
