# Configuration Guide

Complete reference for configuring the Gagiteck AI SaaS Platform.

## Configuration Methods

Configuration can be set via:
1. Environment variables (recommended for secrets)
2. Configuration file (`.env` or `config.yaml`)
3. Runtime API calls

Priority: Environment Variables > Config File > Defaults

---

## Environment Variables

### Core Settings

```bash
# Application
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info

# API
API_VERSION=v1
API_RATE_LIMIT=1000
API_RATE_WINDOW=60000

# Security
JWT_SECRET=your-secret-key-min-32-chars
JWT_EXPIRY=24h
CORS_ORIGINS=https://app.gagiteck.com,https://api.gagiteck.com
```

### Database Configuration

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/gagiteck
DATABASE_POOL_MIN=5
DATABASE_POOL_MAX=20
DATABASE_SSL=true

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
REDIS_TLS=false

# Vector Database
VECTOR_DB_TYPE=pinecone  # or qdrant, weaviate, pgvector
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=gagiteck-embeddings
```

### LLM Provider Keys

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_AI_API_KEY=...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Local Models (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### Storage Configuration

```bash
# Object Storage (S3-compatible)
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=gagiteck-assets
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Local Storage Fallback
LOCAL_STORAGE_PATH=/var/lib/gagiteck/files
```

### Email Configuration

```bash
# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=true
SMTP_USER=noreply@gagiteck.com
SMTP_PASSWORD=...
SMTP_FROM=Gagiteck <noreply@gagiteck.com>
```

---

## Configuration File

### config.yaml

```yaml
# config.yaml
app:
  name: Gagiteck Platform
  environment: production
  debug: false

server:
  host: 0.0.0.0
  port: 3000
  cors:
    origins:
      - https://app.gagiteck.com
      - https://api.gagiteck.com
    credentials: true

api:
  version: v1
  rate_limit:
    requests: 1000
    window_ms: 60000
  pagination:
    default_limit: 20
    max_limit: 100

database:
  url: ${DATABASE_URL}
  pool:
    min: 5
    max: 20
  migrations:
    auto_run: true

redis:
  url: ${REDIS_URL}
  key_prefix: "gagiteck:"

models:
  default: claude-3-opus
  available:
    - id: claude-3-opus
      provider: anthropic
      max_tokens: 4096
      cost_per_1k_input: 0.015
      cost_per_1k_output: 0.075

    - id: claude-3-sonnet
      provider: anthropic
      max_tokens: 4096
      cost_per_1k_input: 0.003
      cost_per_1k_output: 0.015

    - id: gpt-4
      provider: openai
      max_tokens: 8192
      cost_per_1k_input: 0.03
      cost_per_1k_output: 0.06

  routing:
    strategy: cost  # cost, latency, round_robin
    fallback_enabled: true

agents:
  max_per_user: 50
  max_tools_per_agent: 20
  execution:
    timeout_ms: 120000
    max_iterations: 25
    max_tool_calls: 50

workflows:
  max_per_user: 25
  max_steps: 50
  execution:
    timeout_ms: 600000
    retry_attempts: 3
    retry_delay_ms: 5000

storage:
  type: s3  # s3, local, gcs
  s3:
    bucket: ${S3_BUCKET}
    region: ${S3_REGION}
  max_file_size_mb: 100

logging:
  level: info
  format: json
  outputs:
    - type: stdout
    - type: file
      path: /var/log/gagiteck/app.log
      rotation: daily

telemetry:
  enabled: true
  provider: opentelemetry
  endpoint: https://telemetry.gagiteck.com
  sample_rate: 0.1

security:
  encryption:
    algorithm: aes-256-gcm
    key: ${ENCRYPTION_KEY}
  jwt:
    secret: ${JWT_SECRET}
    expiry: 24h
    refresh_expiry: 7d
  api_keys:
    hash_algorithm: argon2
    prefix: ggt_
```

---

## Model Configuration

### Available Models

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| `claude-3-opus` | Anthropic | 200K | Complex reasoning |
| `claude-3-sonnet` | Anthropic | 200K | Balanced performance |
| `claude-3-haiku` | Anthropic | 200K | Fast responses |
| `gpt-4` | OpenAI | 128K | General purpose |
| `gpt-4-turbo` | OpenAI | 128K | Cost-effective |
| `gpt-3.5-turbo` | OpenAI | 16K | Simple tasks |

### Model Routing

```yaml
models:
  routing:
    strategy: smart
    rules:
      # Use cheaper model for simple queries
      - condition: "tokens < 500 AND complexity == 'low'"
        model: gpt-3.5-turbo

      # Use Opus for complex reasoning
      - condition: "task_type == 'reasoning'"
        model: claude-3-opus

      # Use Sonnet for code
      - condition: "task_type == 'code'"
        model: claude-3-sonnet

      # Default fallback
      - condition: "default"
        model: claude-3-sonnet
```

---

## Security Configuration

### Authentication

```yaml
auth:
  # Session-based auth
  session:
    secret: ${SESSION_SECRET}
    max_age: 86400000  # 24 hours

  # JWT auth
  jwt:
    secret: ${JWT_SECRET}
    algorithm: HS256
    expiry: 24h
    refresh_enabled: true
    refresh_expiry: 7d

  # API Key auth
  api_keys:
    enabled: true
    prefix: "ggt_"

  # OAuth providers
  oauth:
    google:
      client_id: ${GOOGLE_CLIENT_ID}
      client_secret: ${GOOGLE_CLIENT_SECRET}

    github:
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}

  # Enterprise SSO
  saml:
    enabled: false
    entity_id: https://api.gagiteck.com/saml
    assertion_consumer_service: https://api.gagiteck.com/saml/acs
    idp_metadata_url: ${SAML_IDP_METADATA_URL}
```

### Rate Limiting

```yaml
rate_limit:
  global:
    requests: 10000
    window_ms: 60000

  by_plan:
    free:
      requests: 100
      window_ms: 60000

    pro:
      requests: 1000
      window_ms: 60000

    enterprise:
      requests: 10000
      window_ms: 60000

  by_endpoint:
    "/v1/agents/*/run":
      requests: 60
      window_ms: 60000
```

---

## Tenant Configuration

### Multi-tenant Settings

```yaml
tenants:
  isolation: database  # database, schema, row

  default_limits:
    agents: 10
    workflows: 5
    api_calls_per_month: 10000
    storage_gb: 5

  plans:
    free:
      agents: 3
      workflows: 1
      api_calls_per_month: 1000
      storage_gb: 1

    pro:
      agents: 25
      workflows: 10
      api_calls_per_month: 50000
      storage_gb: 25

    enterprise:
      agents: unlimited
      workflows: unlimited
      api_calls_per_month: unlimited
      storage_gb: 500
```

---

## Feature Flags

```yaml
features:
  # Beta features
  multi_agent_collaboration:
    enabled: true
    rollout_percentage: 50

  visual_workflow_builder:
    enabled: false

  # Enterprise features
  sso_saml:
    enabled: true
    plans: [enterprise]

  audit_logs:
    enabled: true
    plans: [pro, enterprise]

  custom_models:
    enabled: true
    plans: [enterprise]
```

---

## Environment-Specific Configuration

### Development

```bash
# .env.development
NODE_ENV=development
LOG_LEVEL=debug
DATABASE_URL=postgresql://localhost:5432/gagiteck_dev
REDIS_URL=redis://localhost:6379/0
```

### Staging

```bash
# .env.staging
NODE_ENV=staging
LOG_LEVEL=info
DATABASE_URL=postgresql://staging-db:5432/gagiteck
REDIS_URL=redis://staging-redis:6379/0
```

### Production

```bash
# .env.production
NODE_ENV=production
LOG_LEVEL=warn
DATABASE_URL=postgresql://prod-db-cluster:5432/gagiteck
REDIS_URL=redis://prod-redis-cluster:6379/0
```

---

## Related Documentation

- [Installation Guide](installation.md)
- [Security Guide](security.md)
- [Deployment Guide](deployment-docker.md)
