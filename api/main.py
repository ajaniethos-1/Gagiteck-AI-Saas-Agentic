"""Gagiteck REST API - Main Application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.routes import agents, workflows, executions, health, auth, webhooks, search, rbac
from api.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Sentry if DSN is configured
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        send_default_pii=False,
    )
    logger.info("Sentry error tracking initialized")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting Gagiteck API v{settings.VERSION} ({settings.ENVIRONMENT})")

    # Initialize database
    try:
        from api.db import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    # Initialize Redis cache
    try:
        from api.services.cache import get_cache
        await get_cache()
        logger.info("Redis cache connected")
    except Exception as e:
        logger.warning(f"Redis connection skipped: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Gagiteck API")

    # Close database
    try:
        from api.db import close_db
        await close_db()
        logger.info("Database connection closed")
    except Exception:
        pass

    # Close Redis
    try:
        from api.services.cache import close_cache
        await close_cache()
        logger.info("Redis connection closed")
    except Exception:
        pass


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
            "name": "Authentication",
            "description": "User registration, login, and API key management",
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
        {
            "name": "Webhooks",
            "description": "Configure webhook notifications for events",
        },
        {
            "name": "Search",
            "description": "Search across all resources",
        },
        {
            "name": "Access Control",
            "description": "Roles, permissions, and team management",
        },
    ],
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware (SOC2 compliance)
from api.middleware.security import SecurityHeadersMiddleware, RequestIDMiddleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

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
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/v1/agents", tags=["Agents"])
app.include_router(workflows.router, prefix="/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/v1/executions", tags=["Executions"])
app.include_router(webhooks.router, prefix="/v1/webhooks", tags=["Webhooks"])
app.include_router(search.router, prefix="/v1/search", tags=["Search"])
app.include_router(rbac.router, prefix="/v1/access", tags=["Access Control"])


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
