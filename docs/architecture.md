# Architecture Overview

This document describes the architecture of the Gagiteck AI SaaS Platform.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│    Web App          Mobile Apps         CLI           Third-Party       │
│    (React)          (React Native)      (Node.js)     Integrations      │
└────────────┬───────────────┬──────────────┬─────────────────┬───────────┘
             │               │              │                 │
             ▼               ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Auth      │  │   Rate      │  │   Request   │  │   Load      │    │
│  │   Middleware│  │   Limiting  │  │   Routing   │  │   Balancer  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE SERVICES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  Agent Service  │  │ Workflow Engine │  │ Integration Hub │         │
│  │                 │  │                 │  │                 │         │
│  │ • Agent CRUD    │  │ • DAG Executor  │  │ • Connectors    │         │
│  │ • Execution     │  │ • Scheduling    │  │ • Webhooks      │         │
│  │ • Tool Dispatch │  │ • State Machine │  │ • OAuth Manager │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│           ▼                    ▼                    ▼                   │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                    MESSAGE QUEUE (Redis)                     │       │
│  │  • Job Queue  • Event Bus  • Pub/Sub  • Task Scheduling     │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI LAYER                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   LLM Router    │  │  Tool Runtime   │  │ Memory Manager  │         │
│  │                 │  │                 │  │                 │         │
│  │ • Model Select  │  │ • Sandbox Exec  │  │ • Conversation  │         │
│  │ • Load Balance  │  │ • Code Runner   │  │ • Long-term     │         │
│  │ • Fallback      │  │ • API Caller    │  │ • RAG Retrieval │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│           ▼                    ▼                    ▼                   │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                    LLM PROVIDERS                             │       │
│  │  OpenAI  │  Anthropic  │  Google  │  Local Models           │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   PostgreSQL    │  │    Redis        │  │   Vector DB     │         │
│  │                 │  │                 │  │   (Pinecone/    │         │
│  │ • Users         │  │ • Sessions      │  │    Qdrant)      │         │
│  │ • Agents        │  │ • Cache         │  │                 │         │
│  │ • Workflows     │  │ • Rate Limits   │  │ • Embeddings    │         │
│  │ • Audit Logs    │  │ • Job Queue     │  │ • Similarity    │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐                               │
│  │   Object Store  │  │   Search Index  │                               │
│  │   (S3/MinIO)    │  │   (Elasticsearch│                               │
│  │                 │  │    /Meilisearch)│                               │
│  │ • Files         │  │ • Full-text     │                               │
│  │ • Artifacts     │  │ • Analytics     │                               │
│  └─────────────────┘  └─────────────────┘                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Agent Service

The Agent Service manages the lifecycle of AI agents.

**Responsibilities:**
- Create, update, delete agents
- Configure agent models and parameters
- Dispatch tool calls
- Manage agent execution

**Key Classes:**
```
src/services/
├── AgentService.ts      # Agent CRUD operations
├── ExecutionEngine.ts   # Run agent conversations
├── ToolDispatcher.ts    # Route tool calls
└── PromptBuilder.ts     # Construct system prompts
```

### 2. Workflow Engine

Orchestrates multi-step automated processes.

**Features:**
- DAG-based execution
- Conditional branching
- Parallel execution
- Error handling & retries
- State persistence

**Workflow Definition:**
```yaml
steps:
  - id: step1
    agent: agent-a

  - id: step2a
    agent: agent-b
    depends_on: [step1]

  - id: step2b
    agent: agent-c
    depends_on: [step1]

  - id: step3
    agent: agent-d
    depends_on: [step2a, step2b]
```

### 3. Integration Hub

Connects external services and APIs.

**Connector Types:**
- **OAuth Apps**: Slack, GitHub, Google
- **Webhooks**: Inbound event triggers
- **APIs**: REST, GraphQL clients
- **Databases**: Direct DB connections

### 4. LLM Router

Intelligent model selection and routing.

**Capabilities:**
- Cost-based routing
- Latency optimization
- Automatic fallback
- Load balancing
- Token tracking

```python
# Example routing configuration
router_config = {
    "default": "claude-3-opus",
    "fallback": ["gpt-4", "claude-3-sonnet"],
    "routing_rules": [
        {"if": "tokens > 100000", "use": "claude-3-sonnet"},
        {"if": "task == 'code'", "use": "gpt-4"}
    ]
}
```

---

## Data Flow

### Agent Execution Flow

```
1. Client Request
   └─► API Gateway (Auth + Rate Limit)
       └─► Agent Service (Load Agent Config)
           └─► Prompt Builder (Construct Messages)
               └─► LLM Router (Select Model)
                   └─► LLM Provider (Generate Response)
                       └─► Tool Dispatcher (If tool call)
                           └─► Tool Runtime (Execute)
                               └─► Agent Service (Continue)
                                   └─► Response to Client
```

### Workflow Execution Flow

```
1. Trigger Event
   └─► Workflow Engine (Load DAG)
       └─► Scheduler (Order Steps)
           └─► For each step:
               ├─► Agent Service (Run Agent)
               ├─► State Manager (Save State)
               └─► Next Step (If dependencies met)
           └─► Completion Handler
               └─► Webhook/Callback
```

---

## Security Architecture

### Authentication Layers

```
┌─────────────────────────────────────────┐
│           Authentication Flow            │
├─────────────────────────────────────────┤
│                                          │
│  1. API Key Authentication               │
│     └─► Header: Authorization: Bearer    │
│                                          │
│  2. OAuth 2.0 / OIDC                     │
│     └─► JWT Token Validation             │
│                                          │
│  3. SSO / SAML (Enterprise)              │
│     └─► Identity Provider Integration    │
│                                          │
└─────────────────────────────────────────┘
```

### Authorization Model

Role-Based Access Control (RBAC):

| Role | Agents | Workflows | Settings | Billing |
|------|--------|-----------|----------|---------|
| Owner | Full | Full | Full | Full |
| Admin | Full | Full | Read/Write | Read |
| Developer | Create/Run | Create/Run | Read | - |
| Viewer | Run | View | - | - |

---

## Scalability

### Horizontal Scaling

```
                    Load Balancer
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     ┌─────────┐    ┌─────────┐    ┌─────────┐
     │ API Pod │    │ API Pod │    │ API Pod │
     └────┬────┘    └────┬────┘    └────┬────┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                    Redis Cluster
                    (Shared State)
```

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API Latency (p50) | < 100ms | Excluding LLM time |
| API Latency (p99) | < 500ms | Excluding LLM time |
| Throughput | 10,000 RPS | Per instance |
| Concurrent Agents | 1,000 | Per tenant |

---

## Deployment Options

### Cloud Native (Kubernetes)

```yaml
# Recommended production setup
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: gagiteck-api
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
```

### Self-Hosted

See [Deployment Guide](deployment-docker.md) for Docker Compose setup.

---

## Related Documentation

- [API Reference](api-reference.md)
- [Security Guide](security.md)
- [Deployment Guide](deployment-docker.md)
