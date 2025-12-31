# API Reference

Complete REST API documentation for the Gagiteck AI SaaS Platform.

## Base URL

```
Production: https://api.gagiteck.com/v1
Staging:    https://api-staging.gagiteck.com/v1
Local:      http://localhost:8000/v1
```

## Authentication

All API requests require authentication via API key or JWT token.

### API Key (Header)
```bash
curl -H "Authorization: Bearer ggt_your_api_key" \
  https://api.gagiteck.com/v1/agents
```

### API Key (Query Parameter)
```bash
curl "https://api.gagiteck.com/v1/agents?api_key=ggt_your_api_key"
```

---

## Agents

### List Agents

```http
GET /agents
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results (default: 20, max: 100) |
| `offset` | integer | Pagination offset |
| `status` | string | Filter by status: `active`, `archived` |
| `tags` | string | Comma-separated tag filter |

**Response:**
```json
{
  "data": [
    {
      "id": "agent_abc123",
      "name": "Customer Support",
      "model": "claude-3-opus",
      "status": "active",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

---

### Create Agent

```http
POST /agents
```

**Request Body:**
```json
{
  "name": "Research Assistant",
  "model": "claude-3-opus",
  "system_prompt": "You are a helpful research assistant.",
  "temperature": 0.7,
  "max_tokens": 4096,
  "tools": ["web_search", "read_file"],
  "memory_enabled": true,
  "memory_type": "conversation",
  "tags": ["research", "production"]
}
```

**Response:**
```json
{
  "id": "agent_xyz789",
  "name": "Research Assistant",
  "model": "claude-3-opus",
  "system_prompt": "You are a helpful research assistant.",
  "temperature": 0.7,
  "max_tokens": 4096,
  "tools": ["web_search", "read_file"],
  "memory_enabled": true,
  "memory_type": "conversation",
  "status": "active",
  "created_at": "2025-01-15T12:00:00Z"
}
```

---

### Get Agent

```http
GET /agents/{agent_id}
```

**Response:**
```json
{
  "id": "agent_xyz789",
  "name": "Research Assistant",
  "model": "claude-3-opus",
  "system_prompt": "You are a helpful research assistant.",
  "temperature": 0.7,
  "max_tokens": 4096,
  "tools": ["web_search", "read_file"],
  "memory_enabled": true,
  "memory_type": "conversation",
  "status": "active",
  "stats": {
    "total_executions": 1234,
    "avg_response_time_ms": 2500,
    "success_rate": 0.98
  },
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

---

### Update Agent

```http
PATCH /agents/{agent_id}
```

**Request Body:**
```json
{
  "name": "Updated Research Assistant",
  "temperature": 0.5
}
```

---

### Delete Agent

```http
DELETE /agents/{agent_id}
```

**Response:**
```json
{
  "id": "agent_xyz789",
  "deleted": true
}
```

---

### Run Agent

```http
POST /agents/{agent_id}/run
```

**Request Body:**
```json
{
  "message": "Search for the latest AI research papers on multi-agent systems",
  "context": {
    "user_id": "user_123",
    "session_id": "sess_456"
  },
  "stream": false
}
```

**Response:**
```json
{
  "id": "exec_abc123",
  "agent_id": "agent_xyz789",
  "status": "completed",
  "input": "Search for the latest AI research papers on multi-agent systems",
  "output": "I found several recent papers on multi-agent systems...",
  "tool_calls": [
    {
      "tool": "web_search",
      "input": {"query": "multi-agent systems AI research 2025"},
      "output": {"results": [...]},
      "duration_ms": 1200
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 450,
    "total_tokens": 600
  },
  "duration_ms": 3500,
  "created_at": "2025-01-15T15:00:00Z"
}
```

---

### Run Agent (Streaming)

```http
POST /agents/{agent_id}/run
Content-Type: application/json

{
  "message": "Write a blog post about AI",
  "stream": true
}
```

**Response (Server-Sent Events):**
```
event: start
data: {"id": "exec_abc123", "status": "started"}

event: token
data: {"content": "Artificial"}

event: token
data: {"content": " Intelligence"}

event: token
data: {"content": " has"}

event: tool_call
data: {"tool": "web_search", "status": "started"}

event: tool_call
data: {"tool": "web_search", "status": "completed", "result": {...}}

event: done
data: {"id": "exec_abc123", "status": "completed", "usage": {...}}
```

---

## Conversations

### Create Conversation

```http
POST /conversations
```

**Request Body:**
```json
{
  "agent_id": "agent_xyz789",
  "metadata": {
    "user_id": "user_123",
    "channel": "web"
  }
}
```

**Response:**
```json
{
  "id": "conv_abc123",
  "agent_id": "agent_xyz789",
  "messages": [],
  "created_at": "2025-01-15T15:00:00Z"
}
```

---

### Send Message

```http
POST /conversations/{conversation_id}/messages
```

**Request Body:**
```json
{
  "content": "Hello, I need help with my order"
}
```

**Response:**
```json
{
  "id": "msg_xyz789",
  "role": "assistant",
  "content": "Hello! I'd be happy to help you with your order. Could you please provide your order number?",
  "created_at": "2025-01-15T15:01:00Z"
}
```

---

### Get Conversation History

```http
GET /conversations/{conversation_id}/messages
```

**Response:**
```json
{
  "data": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Hello, I need help",
      "created_at": "2025-01-15T15:00:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Hello! How can I help you today?",
      "created_at": "2025-01-15T15:00:05Z"
    }
  ]
}
```

---

## Workflows

### List Workflows

```http
GET /workflows
```

### Create Workflow

```http
POST /workflows
```

**Request Body:**
```json
{
  "name": "Customer Onboarding",
  "description": "Automated customer onboarding workflow",
  "trigger": {
    "type": "event",
    "event": "customer.created"
  },
  "steps": [
    {
      "id": "verify",
      "name": "Verify Email",
      "agent_id": "agent_verification",
      "input": "Send verification email to {{customer.email}}"
    },
    {
      "id": "welcome",
      "name": "Send Welcome",
      "agent_id": "agent_comms",
      "input": "Send welcome message to {{customer.name}}",
      "depends_on": ["verify"]
    }
  ]
}
```

---

### Trigger Workflow

```http
POST /workflows/{workflow_id}/trigger
```

**Request Body:**
```json
{
  "inputs": {
    "customer": {
      "id": "cust_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Response:**
```json
{
  "id": "run_abc123",
  "workflow_id": "wf_xyz789",
  "status": "running",
  "steps": [
    {"id": "verify", "status": "pending"},
    {"id": "welcome", "status": "pending"}
  ],
  "started_at": "2025-01-15T16:00:00Z"
}
```

---

### Get Workflow Run

```http
GET /workflows/runs/{run_id}
```

**Response:**
```json
{
  "id": "run_abc123",
  "workflow_id": "wf_xyz789",
  "status": "completed",
  "steps": [
    {
      "id": "verify",
      "status": "completed",
      "output": "Email sent successfully",
      "duration_ms": 1500
    },
    {
      "id": "welcome",
      "status": "completed",
      "output": "Welcome message sent",
      "duration_ms": 2000
    }
  ],
  "started_at": "2025-01-15T16:00:00Z",
  "completed_at": "2025-01-15T16:00:05Z"
}
```

---

## Tools

### List Available Tools

```http
GET /tools
```

**Response:**
```json
{
  "data": [
    {
      "name": "web_search",
      "description": "Search the web for information",
      "parameters": {
        "query": {"type": "string", "required": true},
        "limit": {"type": "integer", "default": 10}
      }
    },
    {
      "name": "read_file",
      "description": "Read contents of a file",
      "parameters": {
        "path": {"type": "string", "required": true}
      }
    }
  ]
}
```

### Create Custom Tool

```http
POST /tools
```

**Request Body:**
```json
{
  "name": "get_weather",
  "description": "Get current weather for a city",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "City name"},
      "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "required": ["city"]
  },
  "implementation": {
    "type": "webhook",
    "url": "https://api.example.com/weather",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{secrets.WEATHER_API_KEY}}"
    }
  }
}
```

---

## Errors

### Error Response Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request body is missing required field: name",
    "details": {
      "field": "name",
      "type": "required"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Request validation failed |
| `unauthorized` | 401 | Missing or invalid authentication |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limited` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

---

## Rate Limits

| Plan | Requests/min | Concurrent |
|------|--------------|------------|
| Free | 60 | 5 |
| Pro | 600 | 25 |
| Enterprise | 6000 | 100 |

Rate limit headers:
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1705334400
```

---

## Webhooks

### Webhook Events

| Event | Description |
|-------|-------------|
| `agent.created` | Agent was created |
| `agent.updated` | Agent was updated |
| `agent.deleted` | Agent was deleted |
| `execution.completed` | Agent execution finished |
| `execution.failed` | Agent execution failed |
| `workflow.completed` | Workflow run finished |
| `workflow.failed` | Workflow run failed |

### Webhook Payload

```json
{
  "id": "evt_abc123",
  "type": "execution.completed",
  "data": {
    "execution_id": "exec_xyz789",
    "agent_id": "agent_123",
    "status": "completed"
  },
  "created_at": "2025-01-15T16:00:00Z"
}
```

---

## SDKs

Official SDK libraries:
- [Python SDK](sdk-python.md)
- [Node.js SDK](sdk-nodejs.md)
- [Go SDK](https://github.com/gagiteck/gagiteck-go)
