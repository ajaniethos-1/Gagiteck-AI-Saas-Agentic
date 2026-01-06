"""Pytest configuration and fixtures."""

import os
import pytest

# Set test environment variables before importing app
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Environment is already set above
    yield
    # Cleanup if needed
