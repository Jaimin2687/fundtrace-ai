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
    import os
    settings = get_settings()
    
    # Startup
    print("\n" + "="*60)
    print("FUNDTRACE AI - STARTING UP")
    print("="*60)
    
    # Step 1: Initialize Neo4j driver (fail fast if cannot connect)
    try:
        driver = get_driver()
        app.state.neo4j_driver = driver
        print("✓ Step 1: Neo4j driver initialized")
        print(f"  Connected to: {settings.NEO4J_URI}")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: Cannot connect to Neo4j")
        print(f"  Error: {str(e)}")
        print(f"\n  Please ensure:")
        print(f"  1. Neo4j is running: neo4j start")
        print(f"  2. URI is correct: {settings.NEO4J_URI}")
        print(f"  3. Credentials are valid (user: {settings.NEO4J_USER})")
        print(f"\n  Or use Docker:")
        print(f"  docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:5")
        print("="*60 + "\n")
        raise
    
    # Step 2: Check if model exists
    model_path = 'data/fraud_model.json'
    if not os.path.exists(model_path):
        print(f"\n⚠ WARNING: ML model not found at {model_path}")
        print(f"  The ML worker will not start until you:")
        print(f"  1. Run: python data/ingest.py")
        print(f"  2. Run: python backend/worker/ml_worker.py --train")
        print(f"\n  Backend will still start, but ML features will be disabled.")
        model_exists = False
    else:
        print(f"✓ Step 2: ML model found at {model_path}")
        model_exists = True
    
    # Step 3: Start background workers
    if model_exists:
        try:
            from .worker import ml_worker
            
            # Start alert broadcaster
            broadcaster_task = asyncio.create_task(stream.alert_broadcaster())
            _worker_tasks.append(broadcaster_task)
            print("✓ Step 3a: Alert broadcaster started")
            
            # Start transaction scoring worker
            worker_task = asyncio.create_task(
                ml_worker.run_worker(driver, stream.alert_queue)
            )
            _worker_tasks.append(worker_task)
            print("✓ Step 3b: Transaction scoring worker started")
            
            # Start PaySim alert streamer
            paysim_task = asyncio.create_task(
                ml_worker.stream_paysim_alerts(stream.alert_queue)
            )
            _worker_tasks.append(paysim_task)
            print("✓ Step 3c: PaySim alert streamer started")
            
        except Exception as e:
            print(f"⚠ Warning: ML worker tasks failed to start: {str(e)}")
            print("  Backend will continue without ML features")
    else:
        print("⚠ Step 3: Skipping ML workers (model not trained)")
    
    # Step 4: Ready
    print("\n" + "="*60)
    print("✅ FundTrace AI running at http://localhost:8000")
    print("="*60)
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Health: http://localhost:8000/")
    print("  • Frontend: http://localhost:3000/dashboard")
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
