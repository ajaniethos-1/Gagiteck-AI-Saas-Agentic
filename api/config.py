"""API Configuration."""

from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development, staging, production

    # Security
    API_KEY_PREFIX: str = "ggt_"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://app.gagiteck.com",
        "https://app.mimoai.co",
    ]

    # Database (RDS PostgreSQL)
    DATABASE_URL: str = "postgresql://localhost:5432/gagiteck"

    # Redis (ElastiCache)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # Default cache TTL in seconds

    # AWS SES Email
    AWS_REGION: str = "us-east-1"
    SES_SENDER_EMAIL: str = "noreply@mimoai.co"

    # Sentry Error Tracking
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of requests traced

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
