"""
Configuration management for Phase 3 Backend.

Loads environment variables and provides typed configuration objects.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # OpenAI
    openai_api_key: str

    # Authentication (must match Phase 2)
    jwt_secret: str
    jwt_algorithm: str = "EdDSA"

    # Service URLs
    mcp_server_url: str
    phase2_backend_url: str = "http://localhost:8000"

    # Server
    port: int = 8001
    environment: str = "development"
    log_level: str = "INFO"

    # CORS (can be comma-separated string or list)
    cors_origins: Union[List[str], str] = "http://localhost:3000,http://localhost:3001"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
