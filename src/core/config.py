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

    # AWS S3 Configuration
    S3_BUCKET_NAME: str = Field(
        default="resume-documents",
        description="S3 bucket name for document storage",
    )

    S3_REGION: str = Field(
        default="us-east-1",
        description="AWS region for S3 bucket",
    )

    AWS_ACCESS_KEY_ID: str = Field(
        default="",
        description="AWS access key ID",
    )

    AWS_SECRET_ACCESS_KEY: str = Field(
        default="",
        description="AWS secret access key",
    )

    # ClamAV Configuration
    CLAMAV_HOST: str = Field(
        default="localhost",
        description="ClamAV daemon hostname",
    )

    CLAMAV_PORT: int = Field(
        default=3310,
        description="ClamAV daemon port",
    )

    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(
        default=10485760,  # 10MB in bytes
        description="Maximum file size for uploads in bytes",
    )

    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # noqa: E501
            "application/msword",
            "text/plain",
        ],
        description="List of allowed MIME types for file uploads",
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and session storage",
    )

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL for task queue",
    )

    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL for task results",
    )

    CELERY_TASK_SERIALIZER: str = Field(
        default="json",
        description="Celery task serialization format",
    )

    CELERY_ACCEPT_CONTENT: List[str] = Field(
        default=["json"],
        description="List of content types accepted by Celery",
    )

    CELERY_RESULT_SERIALIZER: str = Field(
        default="json",
        description="Celery result serialization format",
    )

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for GPT-4 access",
    )

    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="OpenAI model to use for generation",
    )

    # AI Service Configuration
    AI_GENERATION_ENABLED: bool = Field(
        default=True,
        description="Enable/disable AI generation features",
    )

    AI_RATE_LIMIT_FREE: int = Field(
        default=10,
        description="AI API rate limit for free tier users (requests per hour)",
    )

    AI_RATE_LIMIT_PREMIUM: int = Field(
        default=100,
        description="AI API rate limit for premium tier users (requests per hour)",
    )

    AI_RATE_LIMIT_ENTERPRISE: int = Field(
        default=1000,
        description="AI API rate limit for enterprise tier users (requests per hour)",
    )

    AI_COST_ALERT_THRESHOLD: float = Field(
        default=100.0,
        description="Cost threshold in USD for alerting on high AI usage",
    )

    # SendGrid Email Configuration
    SENDGRID_API_KEY: str = Field(
        default="",
        description="SendGrid API key for email notifications",
    )

    SENDGRID_FROM_EMAIL: str = Field(
        default="noreply@example.com",
        description="SendGrid from email address",
    )

    # Notification Configuration
    NOTIFICATIONS_ENABLED: bool = Field(
        default=True,
        description="Enable/disable notification system",
    )

    DIGEST_EMAIL_SCHEDULE: str = Field(
        default="0 8 * * *",
        description="Cron schedule for digest emails (default: 8 AM daily)",
    )


settings = Settings()
