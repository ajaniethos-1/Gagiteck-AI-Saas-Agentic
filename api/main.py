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
    description="""
## Gagiteck AI SaaS Platform API

Build and deploy autonomous AI agents with powerful workflow automation.

### Features

- **Agents**: Create, configure, and run AI agents with custom tools and memory
- **Workflows**: Design multi-step workflows with conditional logic and parallel execution
- **Executions**: Monitor and manage running agent and workflow executions

### Authentication

All API endpoints require authentication via API key:

```
Authorization: Bearer your-api-key
```

### Rate Limits

- Free tier: 100 requests/minute
- Pro tier: 1000 requests/minute
- Enterprise: Custom limits

### SDKs

- [Python SDK](https://pypi.org/project/gagiteck/)
- [TypeScript SDK](https://www.npmjs.com/package/@gagiteck/sdk) (coming soon)
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Gagiteck Support",
        "url": "https://github.com/ajaniethos-1/Gagiteck-AI-Saas-Agentic",
        "email": "support@gagiteck.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and status endpoints",
        },
        {
            "name": "Agents",
            "description": "Create and manage AI agents with tools and memory",
        },
        {
            "name": "Workflows",
            "description": "Design and trigger multi-step automation workflows",
        },
        {
            "name": "Executions",
            "description": "Monitor and control running executions",
        },
    ],
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
