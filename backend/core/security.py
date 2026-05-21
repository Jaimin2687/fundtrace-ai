"""
Security configuration for CORS, authentication, and rate limiting.
"""

from collections import defaultdict, deque
import time
from typing import Deque, Dict

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import Settings, get_settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Uses CORS_ORIGINS from settings to allow cross-origin requests.
    """
    origins = settings.CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "x-api-key"],
        max_age=600,
    )


def verify_api_key(x_api_key: str = Header(None)) -> None:
    """Verify API key from header."""
    settings = get_settings()
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


_rate_limit_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def rate_limiter(limit: int, window_seconds: int) -> Depends:
    """Create a simple in-memory rate limit dependency."""

    async def _limit(request: Request) -> None:
        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        now = time.time()
        bucket = _rate_limit_buckets[key]

        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()

        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        bucket.append(now)

    return Depends(_limit)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Sets baseline security headers on all responses."""

    def __init__(self, app: FastAPI, csp: str) -> None:
        super().__init__(app)
        self._csp = csp

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = self._csp

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        return response
