# Installation Guide

This guide covers all methods for installing the Gagiteck AI SaaS Platform.

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 20 GB SSD
- **OS**: Linux (Ubuntu 22.04+), macOS 13+, Windows 11 with WSL2

### Recommended for Production
- **CPU**: 8+ cores
- **RAM**: 32 GB
- **Storage**: 100 GB NVMe SSD
- **OS**: Linux (Ubuntu 22.04 LTS)

## Prerequisites

### Required Software
- Node.js 20+ or Python 3.11+
- Docker 24+ & Docker Compose 2.20+
- PostgreSQL 15+
- Redis 7+
- Git

### API Keys Required
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)
- Additional provider keys as needed

---

## Installation Methods

### Method 1: Docker Compose (Recommended)

The fastest way to get started with all dependencies included.

```bash
# Clone the repository
git clone https://github.com/gagiteck/gagiteck-assets.git
cd gagiteck-assets

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f
```

Services will be available at:
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentation**: http://localhost:3000/docs

### Method 2: Manual Installation

For development or custom deployments.

#### Step 1: Install Dependencies

```bash
# Clone repository
git clone https://github.com/gagiteck/gagiteck-assets.git
cd gagiteck-assets

# Install Node.js dependencies
npm install

# Or for Python
pip install -r requirements.txt
```

#### Step 2: Database Setup

```bash
# Start PostgreSQL (if not running)
sudo systemctl start postgresql

# Create database
createdb gagiteck

# Run migrations
npm run db:migrate

# Seed initial data (optional)
npm run db:seed
```

#### Step 3: Redis Setup

```bash
# Start Redis (if not running)
sudo systemctl start redis

# Verify connection
redis-cli ping
```

#### Step 4: Start Application

```bash
# Development mode
npm run dev

# Production mode
npm run build
npm start
```

### Method 3: Cloud One-Click Deploy

#### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=gagiteck)

#### Deploy to Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gagiteck/gagiteck-assets)

#### Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/gagiteck/gagiteck-assets)

---

## Verification

After installation, verify the setup:

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### Run Tests

```bash
# Run test suite
npm test

# Run with coverage
npm run test:coverage
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
echo $DATABASE_URL
```

#### Docker Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or use Docker CLI
docker system prune -a
```

---

## Next Steps

- [Quick Start Tutorial](quickstart.md) - Build your first agent
- [Configuration Guide](configuration.md) - Customize settings
- [Architecture Overview](architecture.md) - Understand the system
