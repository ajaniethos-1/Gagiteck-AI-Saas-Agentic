"""Gagiteck REST API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import agents, workflows, executions, health
from api.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting Gagiteck API v{settings.VERSION}")
    yield
    # Shutdown
    print("Shutting down Gagiteck API")


app = FastAPI(
    title="Gagiteck AI SaaS Platform",
    description="REST API for autonomous AI agents and workflow automation",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(agents.router, prefix="/v1/agents", tags=["Agents"])
app.include_router(workflows.router, prefix="/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/v1/executions", tags=["Executions"])


def run():
    """Run the API server."""
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run()
