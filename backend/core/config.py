from functools import lru_cache
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Neo4j Configuration
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_ENCRYPTION: bool = False
    NEO4J_MAX_POOL_SIZE: int = 50
    NEO4J_MAX_CONN_LIFETIME: int = 3600
    
    # API Configuration
    API_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Optional Frontend Configuration
    FRONTEND_ORIGIN: str | None = None
    NEXT_PUBLIC_API_KEY: str | None = None
    NEXT_PUBLIC_API_BASE_URL: str | None = None
    NEXT_PUBLIC_WS_BASE_URL: str | None = None
    STREAM_MOCK_MODE: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
