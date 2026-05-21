from functools import lru_cache
from typing import List
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
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
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Optional Frontend Configuration
    FRONTEND_ORIGIN: str | None = None
    NEXT_PUBLIC_API_KEY: str | None = None
    NEXT_PUBLIC_API_BASE_URL: str | None = None
    NEXT_PUBLIC_WS_BASE_URL: str | None = None
    STREAM_MOCK_MODE: bool = False
    MODEL_SOURCE: str = "auto"
    AUTH_MODE: str = "disabled"
    AUDIT_LOG_PATH: str = "data/audit.log"
    KAFKA_ENABLED: bool = False
    KAFKA_BROKERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "cbs.transactions.raw"
    KAFKA_GROUP_ID: str = "fundtrace-ingest"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: str | None = None
    KAFKA_USERNAME: str | None = None
    KAFKA_PASSWORD: str | None = None
    KAFKA_BATCH_SIZE: int = 200
    KAFKA_POLL_TIMEOUT_MS: int = 1000

    BANK_API_ENABLED: bool = False
    BANK_API_BASE_URL: str | None = None
    BANK_API_ENDPOINT: str = "/transactions/batch"
    BANK_API_AUTH_HEADER: str = "Authorization"
    BANK_API_AUTH_TOKEN: str | None = None
    BANK_API_POLL_INTERVAL_SEC: int = 15
    BANK_API_TIMEOUT_SEC: int = 10
    BANK_API_VERIFY_SSL: bool = True

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("CORS_ORIGINS must contain exactly one origin")
        if any(origin.strip() == "*" for origin in value):
            raise ValueError("CORS_ORIGINS cannot include wildcard origins")
        if len(value) != 1:
            raise ValueError("CORS_ORIGINS must contain exactly one origin")
        return value

    @field_validator("MODEL_SOURCE")
    @classmethod
    def validate_model_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"auto", "elliptic", "paysim"}:
            raise ValueError("MODEL_SOURCE must be one of: auto, elliptic, paysim")
        return normalized

    @field_validator("AUTH_MODE")
    @classmethod
    def validate_auth_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"disabled", "mock", "jwt"}:
            raise ValueError("AUTH_MODE must be one of: disabled, mock, jwt")
        return normalized


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
