# Gagiteck API Reference

## Overview

The Gagiteck API provides programmatic access to the AI SaaS platform. Build and deploy autonomous AI agents, create workflows, and monitor executions.

**Base URL:** `https://api.mimoai.co`

**API Version:** v1

## Authentication

All API requests require authentication using either a Bearer token (JWT) or API key.

### Bearer Token (JWT)

```bash
curl -X GET "https://api.mimoai.co/v1/agents" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### API Key

```bash
curl -X GET "https://api.mimoai.co/v1/agents" \
  -H "Authorization: Bearer ggt_your_api_key_here"
```

### Obtaining Credentials

1. **JWT Token:** Call `POST /v1/auth/login` with email and password
2. **API Key:** Create via `POST /v1/auth/api-keys` or in the dashboard Settings

---

## Rate Limits

| Tier | Requests/Minute | Concurrent |
|------|-----------------|------------|
| Free | 100 | 5 |
| Pro | 1,000 | 25 |
| Enterprise | Custom | Custom |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Endpoints

### Authentication

#### Sign Up
```http
POST /v1/auth/signup
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login
```http
POST /v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Get Current User
```http
GET /v1/auth/me
```

**Response:** `200 OK`
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

#### Create API Key
```http
POST /v1/auth/api-keys
```

**Request Body:**
```json
{
  "name": "Production Key"
}
```

**Response:** `201 Created`
```json
{
  "id": "key_xyz789",
  "name": "Production Key",
  "key": "ggt_live_abc123xyz...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

> **Important:** The `key` is only returned once. Store it securely.

---

### Agents

#### List Agents
```http
GET /v1/agents?limit=20&offset=0
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 20 | Max results (1-100) |
| offset | integer | 0 | Skip N results |

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "agent_abc123",
      "name": "Research Assistant",
      "system_prompt": "You are a helpful research assistant...",
      "config": {
        "model": "claude-3-sonnet",
        "max_tokens": 4096,
        "temperature": 0.7
      },
      "tools": ["web_search", "calculator"],
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 12,
  "limit": 20,
  "offset": 0
}
```

#### Create Agent
```http
POST /v1/agents
```

**Request Body:**
```json
{
  "name": "Customer Support Bot",
  "system_prompt": "You are a helpful customer support agent for Acme Corp...",
  "config": {
    "model": "claude-3-sonnet",
    "max_tokens": 4096,
    "temperature": 0.7,
    "max_iterations": 25,
    "timeout_ms": 120000
  },
  "tools": ["knowledge_base", "ticket_system"],
  "metadata": {
    "department": "support",
    "priority": "high"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "agent_def456",
  "name": "Customer Support Bot",
  "system_prompt": "You are a helpful customer support agent...",
  "config": {...},
  "tools": ["knowledge_base", "ticket_system"],
  "metadata": {"department": "support"},
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Agent
```http
GET /v1/agents/{agent_id}
```

**Response:** `200 OK` - Returns agent object

#### Update Agent
```http
PATCH /v1/agents/{agent_id}
```

**Request Body:** (partial update)
```json
{
  "name": "Updated Agent Name",
  "config": {
    "temperature": 0.5
  }
}
```

#### Delete Agent
```http
DELETE /v1/agents/{agent_id}
```

**Response:** `204 No Content`

#### Run Agent
```http
POST /v1/agents/{agent_id}/run
```

**Request Body:**
```json
{
  "message": "What are the latest news about AI?",
  "context": {
    "user_id": "user_123",
    "session_id": "sess_456"
  },
  "stream": false
}
```

**Response:** `200 OK`
```json
{
  "id": "run_xyz789",
  "agent_id": "agent_abc123",
  "content": "Here are the latest AI news...",
  "model": "claude-3-sonnet",
  "tool_calls": [
    {
      "id": "call_1",
      "name": "web_search",
      "arguments": {"query": "latest AI news"},
      "result": "..."
    }
  ],
  "usage": {
    "input_tokens": 150,
    "output_tokens": 500
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Workflows

#### List Workflows
```http
GET /v1/workflows?limit=20&offset=0
```

#### Create Workflow
```http
POST /v1/workflows
```

**Request Body:**
```json
{
  "name": "Content Pipeline",
  "description": "Generate and publish blog content",
  "steps": [
    {
      "id": "step_1",
      "type": "agent",
      "name": "Research",
      "config": {
        "agent_id": "agent_abc123",
        "message": "Research the topic: {{input.topic}}"
      }
    },
    {
      "id": "step_2",
      "type": "agent",
      "name": "Write",
      "config": {
        "agent_id": "agent_def456",
        "message": "Write an article based on: {{step_1.output}}"
      }
    },
    {
      "id": "step_3",
      "type": "webhook",
      "name": "Publish",
      "config": {
        "url": "https://api.blog.com/posts",
        "method": "POST",
        "body": {"content": "{{step_2.output}}"}
      }
    }
  ]
}
```

#### Trigger Workflow
```http
POST /v1/workflows/{workflow_id}/trigger
```

**Request Body:**
```json
{
  "input": {
    "topic": "The future of AI agents"
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "exec_abc123",
  "type": "workflow",
  "resource_id": "workflow_xyz",
  "status": "running",
  "started_at": "2024-01-15T10:30:00Z"
}
```

---

### Executions

#### List Executions
```http
GET /v1/executions?limit=20&offset=0&status=running
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Max results |
| offset | integer | Skip N results |
| status | string | Filter by status |

#### Get Execution
```http
GET /v1/executions/{execution_id}
```

**Response:** `200 OK`
```json
{
  "id": "exec_abc123",
  "type": "agent",
  "resource_id": "agent_xyz",
  "status": "completed",
  "result": {...},
  "error": null,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:45Z"
}
```

#### Cancel Execution
```http
POST /v1/executions/{execution_id}/cancel
```

---

### Webhooks

#### List Webhooks
```http
GET /v1/webhooks
```

#### Create Webhook
```http
POST /v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["execution.completed", "execution.failed"],
  "secret": "your_webhook_secret"
}
```

#### List Available Events
```http
GET /v1/webhooks/events
```

**Response:**
```json
{
  "events": [
    "agent.created",
    "agent.updated",
    "agent.deleted",
    "workflow.created",
    "workflow.updated",
    "workflow.deleted",
    "execution.started",
    "execution.completed",
    "execution.failed",
    "execution.cancelled"
  ]
}
```

#### Test Webhook
```http
POST /v1/webhooks/{webhook_id}/test
```

---

### Search

#### Search Resources
```http
GET /v1/search?q=customer+support&types=agent,workflow
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Search query |
| types | string | Comma-separated types |
| status | string | Filter by status |
| limit | integer | Max results |

---

### Access Control (RBAC)

#### List Roles
```http
GET /v1/access/roles
```

#### Get Team
```http
GET /v1/access/team
```

#### Invite Team Member
```http
POST /v1/access/team/members
```

**Request Body:**
```json
{
  "email": "teammate@company.com",
  "role_id": "role_developer"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE",
  "status": 400
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | BAD_REQUEST | Invalid request body |
| 401 | UNAUTHORIZED | Missing or invalid auth |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---

## SDKs

### Python

```bash
pip install gagiteck
```

```python
from gagiteck import Gagiteck

client = Gagiteck(api_key="ggt_your_key")

# Create an agent
agent = client.agents.create(
    name="My Agent",
    system_prompt="You are a helpful assistant"
)

# Run the agent
response = client.agents.run(
    agent.id,
    message="Hello, how can you help?"
)
print(response.content)
```

### TypeScript/JavaScript

```bash
npm install @gagiteck/sdk
```

```typescript
import { Gagiteck } from '@gagiteck/sdk';

const client = new Gagiteck({ apiKey: 'ggt_your_key' });

// Create an agent
const agent = await client.agents.create({
  name: 'My Agent',
  systemPrompt: 'You are a helpful assistant'
});

// Run the agent
const response = await client.agents.run(agent.id, {
  message: 'Hello, how can you help?'
});
console.log(response.content);
```

---

## Webhook Verification

Verify webhook signatures to ensure requests come from Gagiteck:

```python
import hmac
import hashlib

def verify_webhook(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

Webhook headers:
- `X-Webhook-Signature`: HMAC-SHA256 signature
- `X-Webhook-Event`: Event type
- `X-Webhook-ID`: Unique event ID
- `X-Webhook-Timestamp`: ISO timestamp

---

## Interactive Documentation

For interactive API exploration, visit:
- **Swagger UI:** https://api.mimoai.co/docs
- **ReDoc:** https://api.mimoai.co/redoc
- **OpenAPI Spec:** https://api.mimoai.co/openapi.json
