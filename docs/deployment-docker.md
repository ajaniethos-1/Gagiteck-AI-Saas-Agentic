# Docker Deployment Guide

This guide covers deploying the Gagiteck AI SaaS Platform using Docker and Docker Compose.

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8 GB RAM minimum
- 20 GB disk space

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic.git
cd gagiteck-AI-SaaS-Agentic

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your settings:

```bash
# Database
POSTGRES_USER=gagiteck
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=gagiteck
DATABASE_URL=postgresql://gagiteck:your_secure_password@postgres:5432/gagiteck

# Redis
REDIS_URL=redis://redis:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key_here

# AI Provider Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Dashboard
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## Services

The Docker Compose stack includes:

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI backend |
| `dashboard` | 3000 | Next.js frontend |
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache & queues |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌─────────────┐     ┌─────────────┐                   │
│  │  Dashboard  │────▶│     API     │                   │
│  │   :3000     │     │    :8000    │                   │
│  └─────────────┘     └──────┬──────┘                   │
│                              │                          │
│              ┌───────────────┼───────────────┐         │
│              ▼               ▼               ▼          │
│       ┌───────────┐   ┌───────────┐   ┌───────────┐   │
│       │  Postgres │   │   Redis   │   │    S3     │   │
│       │   :5432   │   │   :6379   │   │ (optional)│   │
│       └───────────┘   └───────────┘   └───────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Docker Compose File

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://gagiteck:password@postgres:5432/gagiteck
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      - api
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=gagiteck
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=gagiteck
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## Building Images

### Build All Services

```bash
docker-compose build
```

### Build Individual Service

```bash
# Build API only
docker-compose build api

# Build Dashboard only
docker-compose build dashboard
```

### Build with No Cache

```bash
docker-compose build --no-cache
```

## Managing Services

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart a specific service
docker-compose restart api
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Execute Commands

```bash
# Run database migrations
docker-compose exec api python -m alembic upgrade head

# Access PostgreSQL
docker-compose exec postgres psql -U gagiteck -d gagiteck

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Production Configuration

### Using Production Compose File

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: your-registry/gagiteck-api:latest
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
    environment:
      - NODE_ENV=production
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  dashboard:
    image: your-registry/gagiteck-dashboard:latest
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Checks

Add health checks to your services:

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Updating Deployments

### Pull Latest Images

```bash
docker-compose pull
docker-compose up -d
```

### Zero-Downtime Updates

```bash
# Scale up new containers
docker-compose up -d --scale api=2 --no-recreate

# Remove old containers
docker-compose up -d --scale api=1
```

## Backup & Restore

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U gagiteck gagiteck > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U gagiteck gagiteck < backup.sql
```

### Volume Backup

```bash
# Backup PostgreSQL volume
docker run --rm -v gagiteck_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres-backup.tar.gz /data
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Inspect container
docker inspect gagiteck-api-1
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose exec postgres pg_isready

# Check network connectivity
docker-compose exec api ping postgres
```

### Port Conflicts

```bash
# Find process using port
lsof -i :3000

# Use different ports
API_PORT=8001 DASHBOARD_PORT=3001 docker-compose up -d
```

### Memory Issues

```bash
# Check container memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

## Next Steps

- [AWS Deployment](deployment-cloud.md) - Deploy to AWS with Terraform
- [Kubernetes Deployment](deployment-kubernetes.md) - Production K8s setup
- [Configuration Guide](configuration.md) - Environment configuration
