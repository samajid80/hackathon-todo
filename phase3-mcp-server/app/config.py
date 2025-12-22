"""
Configuration management for Phase 3 MCP Server.

Loads environment variables and provides typed configuration objects.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Phase 2 Backend Configuration
    phase2_backend_url: str = "http://localhost:8000"

    # Authentication (must match Phase 2 and Phase 3 backend)
    jwt_secret: str

    # Server Configuration
    port: int = 8002
    environment: str = "development"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
