"""Application configuration management using Pydantic settings."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: Database connection URL
        SECRET_KEY: Secret key for cryptographic operations
        CORS_ORIGINS: List of allowed CORS origins
        DEBUG: Debug mode flag
        ENVIRONMENT: Application environment (development, staging, production)
        LOG_LEVEL: Logging level
        API_V1_PREFIX: API version 1 prefix
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL",
    )

    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key for cryptographic operations",
    )

    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="List of allowed CORS origins",
    )

    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag",
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment",
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
    )

    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="API version 1 prefix",
    )


settings = Settings()
