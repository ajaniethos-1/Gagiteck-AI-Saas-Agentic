"""API Configuration."""

import secrets
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

logger = logging.getLogger(__name__)


def generate_secure_secret() -> str:
    """Generate a cryptographically secure secret."""
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings."""

    # App
    VERSION: str = "0.2.1"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development, staging, production

    # Security
    API_KEY_PREFIX: str = "ggt_"
    JWT_SECRET: str = ""  # Must be set via environment variable
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # Account Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_MFA_FOR_ADMIN: bool = True

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

    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90

    @field_validator('JWT_SECRET', mode='before')
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        """Validate JWT secret is secure."""
        if not v or v == "change-me-in-production":
            # In development, generate a random secret
            # In production, this should fail or use a secure default
            import os
            if os.getenv("ENVIRONMENT", "development") == "production":
                logger.warning(
                    "JWT_SECRET not set in production! Generating temporary secret. "
                    "Set JWT_SECRET environment variable for security."
                )
            return generate_secure_secret()
        if len(v) < 32:
            logger.warning("JWT_SECRET should be at least 32 characters for security")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
