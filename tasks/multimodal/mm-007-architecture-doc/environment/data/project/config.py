"""Application configuration management.

Loads settings from environment variables with sensible defaults.
Uses Pydantic BaseSettings for validation.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "BlogAPI"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
