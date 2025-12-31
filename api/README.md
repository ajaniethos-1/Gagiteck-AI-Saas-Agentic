# Gagiteck REST API

REST API for the Gagiteck AI SaaS Platform.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn api.main:app --reload

# Or use the CLI
gagiteck-api
```

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /` - API info

### Agents
- `GET /v1/agents` - List agents
- `POST /v1/agents` - Create agent
- `GET /v1/agents/{id}` - Get agent
- `PATCH /v1/agents/{id}` - Update agent
- `DELETE /v1/agents/{id}` - Delete agent
- `POST /v1/agents/{id}/run` - Run agent

### Workflows
- `GET /v1/workflows` - List workflows
- `POST /v1/workflows` - Create workflow
- `GET /v1/workflows/{id}` - Get workflow
- `PATCH /v1/workflows/{id}` - Update workflow
- `DELETE /v1/workflows/{id}` - Delete workflow
- `POST /v1/workflows/{id}/trigger` - Trigger workflow

### Executions
- `GET /v1/executions` - List executions
- `GET /v1/executions/{id}` - Get execution
- `POST /v1/executions/{id}/cancel` - Cancel execution
- `GET /v1/executions/{id}/logs` - Get logs

## Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
