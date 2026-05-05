from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    FRONTEND_ORIGIN: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_MAX_POOL_SIZE: int = 50
    NEO4J_MAX_CONN_LIFETIME: int = 3600
    API_KEY: str
    NEXT_PUBLIC_API_KEY: str | None = None
    NEXT_PUBLIC_API_BASE_URL: str | None = None
    NEXT_PUBLIC_WS_BASE_URL: str | None = None
    STREAM_MOCK_MODE: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
