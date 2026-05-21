"""
FundTrace AI - FastAPI Backend
Main application entry point with proper lifespan management and error handling.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .api.v1 import export, graph, stream, entity, cases, ingest
from .core.config import get_settings
from .core.security import SecurityHeadersMiddleware
from .core.model_registry import get_model_info, model_exists
from .db.neo4j_client import get_driver, close_driver
from .worker import ml_worker
from .services.ingest.bank_ingest import start_kafka_consumer, stop_kafka_consumer
from .services.ingest.bank_api import run_bank_api_poller


# Background task references
_worker_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager: startup and shutdown.
    """
    settings = get_settings()
    
    # ============================================================
    # STARTUP
    # ============================================================
    print("\n" + "="*60)
    print("FUNDTRACE AI - STARTING UP")
    print("="*60)
    
    app.state.neo4j_driver = None

    if settings.STREAM_MOCK_MODE:
        raise RuntimeError("STREAM_MOCK_MODE is enabled. Disable mock mode to use real Neo4j data.")

    # Connect Neo4j
    try:
        driver = get_driver()
        app.state.neo4j_driver = driver
        print("✓ Neo4j driver initialized")
        print(f"  Connected to: {settings.NEO4J_URI}")
    except Exception as exc:
        raise RuntimeError(f"Failed to connect to Neo4j: {exc}") from exc

    # Check model
    model_info = get_model_info()
    if not model_exists(model_info):
        raise RuntimeError(f"ML model not found at {model_info.path}. Train the model before starting.")
    print(f"✓ ML model found: {model_info.path}")
    print(f"  Model source: {model_info.source}")
    
    # Start background workers
    try:
        # Alert broadcaster
        broadcaster_task = asyncio.create_task(stream.alert_broadcaster())
        _worker_tasks.append(broadcaster_task)
        print("✓ Alert broadcaster started")

        # ML worker (real Neo4j scoring)
        worker_task = asyncio.create_task(
            ml_worker.run_worker(driver, stream.alert_queue)
        )
        _worker_tasks.append(worker_task)
        print("✓ ML scoring worker started")

        if settings.KAFKA_ENABLED:
            kafka_task = asyncio.create_task(
                asyncio.to_thread(start_kafka_consumer, driver, settings)
            )
            _worker_tasks.append(kafka_task)
            print("✓ Kafka ingestion consumer started")

        if settings.BANK_API_ENABLED:
            bank_task = asyncio.create_task(
                run_bank_api_poller(stream.alert_queue, settings)
            )
            _worker_tasks.append(bank_task)
            print("✓ Bank API ingestion poller started")
        
    except Exception as e:
        print(f"⚠ Error starting background workers: {e}")
    
    print("="*60)
    print("✅ FundTrace AI ready at http://localhost:8000")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Health: http://localhost:8000/health")
    print("  • WebSocket: ws://localhost:8000/api/v1/stream/alerts")
    print("="*60 + "\n")
    
    yield
    
    # ============================================================
    # SHUTDOWN
    # ============================================================
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

    if settings.KAFKA_ENABLED:
        stop_kafka_consumer()
    
    print("✓ Background tasks cancelled")
    close_driver()
    print("✓ Neo4j driver closed")
    print("="*60 + "\n")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FundTrace AI",
        description="Intelligent Fund Flow Tracking for Fraud Detection",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )
    
    # GZip compression for large graph payloads
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # Security headers middleware with CSP
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    app.add_middleware(SecurityHeadersMiddleware, csp=csp)
    
    # Include routers
    app.include_router(graph.router)
    app.include_router(stream.router)
    app.include_router(export.router)
    app.include_router(entity.router)
    app.include_router(cases.router)
    app.include_router(ingest.router)
    
    # Root health check (no auth required)
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "fundtrace-ai",
            "version": "1.0.0",
        }
    
    @app.get("/")
    async def root():
        return {
            "message": "FundTrace AI Backend",
            "docs": "/docs",
            "health": "/health",
        }
    
    return app


# Create the app instance
app = create_app()
