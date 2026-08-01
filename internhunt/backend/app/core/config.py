"""
Application configuration using Pydantic Settings.

All sensitive values must be supplied via environment variables or a .env file.
No secrets are hardcoded here.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_HOSTS: list[str] = ["*"]

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Supabase ───────────────────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # ── Telegram ───────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    # ── Gmail SMTP ─────────────────────────────────────────────────────────────
    SMTP_EMAIL: str
    SMTP_APP_PASSWORD: str
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # ── AI / Embeddings ────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MATCH_THRESHOLD: float = 0.4

    # ── Crawler ────────────────────────────────────────────────────────────────
    CRAWLER_HEADLESS: bool = True
    CRAWLER_TIMEOUT_MS: int = 30_000
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_CONCURRENCY: int = 5

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()  # type: ignore[call-arg]


settings: Settings = get_settings()
