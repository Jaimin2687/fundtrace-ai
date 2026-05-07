"""
Security configuration for CORS and authentication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Uses CORS_ORIGINS from settings to allow cross-origin requests.
    """
    # Use CORS_ORIGINS if available, fallback to FRONTEND_ORIGIN for backward compatibility
    origins = settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else [settings.FRONTEND_ORIGIN]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "x-api-key"],
        max_age=600,
    )
