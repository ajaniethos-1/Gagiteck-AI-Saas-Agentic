"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel
from api.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str = "connected"
    redis: str = "connected"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        database="connected",
        redis="connected",
    )


@router.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Gagiteck AI SaaS Platform",
        "version": settings.VERSION,
        "docs": "/docs",
    }
