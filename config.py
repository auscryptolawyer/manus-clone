"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Required
    anthropic_api_key: str

    # Browser settings
    browser_headless: bool = True
    screenshot_quality: int = 50

    # Agent limits
    max_steps_per_task: int = 50
    step_timeout_seconds: int = 60

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Future - Redis
    redis_url: str | None = None

    # Future - Sentry
    sentry_dsn: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
