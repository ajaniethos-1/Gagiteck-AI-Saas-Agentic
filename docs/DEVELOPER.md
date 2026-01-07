# Gagiteck Developer Guide

This guide covers integration patterns, SDK usage, and best practices for developers building with Gagiteck.

## Table of Contents

1. [Quick Start](#quick-start)
2. [SDKs](#sdks)
3. [Authentication](#authentication)
4. [Common Patterns](#common-patterns)
5. [Webhooks](#webhooks)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## Quick Start

### 1. Get Your API Key

```bash
# Login and create an API key
curl -X POST https://api.mimoai.co/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Use the token to create an API key
curl -X POST https://api.mimoai.co/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Development Key"}'
```

### 2. Make Your First Request

```bash
curl -X GET https://api.mimoai.co/v1/agents \
  -H "Authorization: Bearer ggt_your_api_key"
```

### 3. Create and Run an Agent

```bash
# Create agent
curl -X POST https://api.mimoai.co/v1/agents \
  -H "Authorization: Bearer ggt_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Agent",
    "system_prompt": "You are a helpful assistant."
  }'

# Run agent (use the returned agent ID)
curl -X POST https://api.mimoai.co/v1/agents/agent_xxx/run \
  -H "Authorization: Bearer ggt_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you do?"}'
```

---

## SDKs

### Python SDK

#### Installation

```bash
pip install gagiteck
```

#### Basic Usage

```python
from gagiteck import Gagiteck

# Initialize client
client = Gagiteck(api_key="ggt_your_api_key")

# List agents
agents = client.agents.list()
for agent in agents.data:
    print(f"{agent.id}: {agent.name}")

# Create agent
agent = client.agents.create(
    name="Support Bot",
    system_prompt="You are a helpful support agent.",
    config={
        "model": "claude-3-sonnet",
        "temperature": 0.7
    },
    tools=["knowledge_base"]
)

# Run agent
response = client.agents.run(
    agent.id,
    message="How do I reset my password?",
    context={"user_id": "user_123"}
)
print(response.content)

# Create workflow
workflow = client.workflows.create(
    name="Support Pipeline",
    steps=[
        {
            "id": "classify",
            "type": "agent",
            "config": {"agent_id": "agent_classifier", "message": "{{input.query}}"}
        },
        {
            "id": "respond",
            "type": "agent",
            "config": {"agent_id": "agent_responder", "message": "{{classify.output}}"}
        }
    ]
)

# Trigger workflow
execution = client.workflows.trigger(
    workflow.id,
    input={"query": "I can't login to my account"}
)
print(f"Execution started: {execution.id}")

# Poll for completion
while execution.status == "running":
    time.sleep(1)
    execution = client.executions.get(execution.id)

print(f"Result: {execution.result}")
```

#### Async Support

```python
import asyncio
from gagiteck import AsyncGagiteck

async def main():
    client = AsyncGagiteck(api_key="ggt_your_api_key")

    # Run multiple agents concurrently
    tasks = [
        client.agents.run(agent_id, message="Query 1"),
        client.agents.run(agent_id, message="Query 2"),
        client.agents.run(agent_id, message="Query 3"),
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        print(result.content)

asyncio.run(main())
```

### TypeScript/JavaScript SDK

#### Installation

```bash
npm install @gagiteck/sdk
# or
yarn add @gagiteck/sdk
```

#### Basic Usage

```typescript
import { Gagiteck } from '@gagiteck/sdk';

// Initialize client
const client = new Gagiteck({ apiKey: 'ggt_your_api_key' });

// List agents
const agents = await client.agents.list();
agents.data.forEach(agent => {
  console.log(`${agent.id}: ${agent.name}`);
});

// Create agent
const agent = await client.agents.create({
  name: 'Support Bot',
  systemPrompt: 'You are a helpful support agent.',
  config: {
    model: 'claude-3-sonnet',
    temperature: 0.7
  }
});

// Run agent
const response = await client.agents.run(agent.id, {
  message: 'How do I reset my password?'
});
console.log(response.content);

// Stream response
const stream = await client.agents.run(agent.id, {
  message: 'Explain quantum computing',
  stream: true
});

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```

#### React Integration

```tsx
import { useGagiteck } from '@gagiteck/react';

function ChatBot() {
  const { run, isLoading, response } = useGagiteck({
    agentId: 'agent_xyz'
  });

  const handleSubmit = async (message: string) => {
    await run({ message });
  };

  return (
    <div>
      <input onSubmit={handleSubmit} />
      {isLoading && <Spinner />}
      {response && <Message content={response.content} />}
    </div>
  );
}
```

---

## Authentication

### API Key Best Practices

```python
import os

# Use environment variables
client = Gagiteck(api_key=os.environ["GAGITECK_API_KEY"])

# Or use a secrets manager
from your_secrets_manager import get_secret
client = Gagiteck(api_key=get_secret("gagiteck-api-key"))
```

### Key Rotation

```python
# Create new key
new_key = client.auth.create_api_key(name="Rotated Key")

# Update your application with new_key.key

# Delete old key
client.auth.delete_api_key(old_key_id)
```

### JWT Token Management

```python
# Login to get JWT
auth = client.auth.login(email="user@example.com", password="password")
access_token = auth.access_token

# Token expires after 24 hours
# Implement refresh logic in your application
```

---

## Common Patterns

### Chatbot with Memory

```python
class ChatSession:
    def __init__(self, client, agent_id):
        self.client = client
        self.agent_id = agent_id
        self.history = []

    def chat(self, message):
        # Include conversation history as context
        response = self.client.agents.run(
            self.agent_id,
            message=message,
            context={
                "conversation_history": self.history[-10:]  # Last 10 messages
            }
        )

        # Update history
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": response.content})

        return response.content

# Usage
session = ChatSession(client, "agent_support")
print(session.chat("Hello!"))
print(session.chat("What did I just say?"))  # Agent remembers context
```

### Batch Processing

```python
import asyncio

async def process_batch(items):
    client = AsyncGagiteck(api_key=API_KEY)

    # Process in batches of 10 to respect rate limits
    batch_size = 10
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [
            client.agents.run(AGENT_ID, message=item)
            for item in batch
        ]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

        # Small delay between batches
        await asyncio.sleep(1)

    return results
```

### Pipeline Pattern

```python
def create_pipeline(client):
    # Step 1: Classifier
    classifier = client.agents.create(
        name="Classifier",
        system_prompt="Classify the input as: question, complaint, or feedback"
    )

    # Step 2: Handlers for each type
    handlers = {
        "question": client.agents.create(
            name="Q&A Bot",
            system_prompt="Answer questions helpfully"
        ),
        "complaint": client.agents.create(
            name="Complaint Handler",
            system_prompt="Handle complaints with empathy"
        ),
        "feedback": client.agents.create(
            name="Feedback Collector",
            system_prompt="Thank for feedback and summarize"
        )
    }

    def process(message):
        # Classify
        classification = client.agents.run(classifier.id, message=message)
        category = classification.content.strip().lower()

        # Route to appropriate handler
        if category in handlers:
            return client.agents.run(handlers[category].id, message=message)
        else:
            return client.agents.run(handlers["question"].id, message=message)

    return process

# Usage
pipeline = create_pipeline(client)
result = pipeline("Why isn't my order arriving?")
```

---

## Webhooks

### Setting Up Webhooks

```python
# Create webhook
webhook = client.webhooks.create(
    url="https://your-server.com/gagiteck-webhook",
    events=["execution.completed", "execution.failed"],
    secret="your_webhook_secret"
)
```

### Handling Webhooks (Flask)

```python
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

def verify_signature(payload, signature):
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.route("/gagiteck-webhook", methods=["POST"])
def handle_webhook():
    # Verify signature
    signature = request.headers.get("X-Webhook-Signature")
    if not verify_signature(request.data, signature):
        abort(401)

    # Parse event
    event = request.json
    event_type = request.headers.get("X-Webhook-Event")

    if event_type == "execution.completed":
        handle_completed(event)
    elif event_type == "execution.failed":
        handle_failed(event)

    return {"status": "ok"}

def handle_completed(event):
    execution_id = event["id"]
    result = event["data"]["result"]
    # Process result...

def handle_failed(event):
    execution_id = event["id"]
    error = event["data"]["error"]
    # Alert team, retry, etc.
```

### Handling Webhooks (Express)

```typescript
import express from 'express';
import crypto from 'crypto';

const app = express();
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

function verifySignature(payload: string, signature: string): boolean {
  const expected = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expected}`),
    Buffer.from(signature)
  );
}

app.post('/gagiteck-webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-webhook-signature'] as string;

  if (!verifySignature(req.body.toString(), signature)) {
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(req.body);
  const eventType = req.headers['x-webhook-event'];

  switch (eventType) {
    case 'execution.completed':
      handleCompleted(event);
      break;
    case 'execution.failed':
      handleFailed(event);
      break;
  }

  res.json({ status: 'ok' });
});
```

---

## Error Handling

### SDK Error Handling

```python
from gagiteck import Gagiteck, GagiteckError, RateLimitError, AuthError

client = Gagiteck(api_key="ggt_your_key")

try:
    response = client.agents.run(agent_id, message="Hello")
except AuthError as e:
    print(f"Authentication failed: {e}")
    # Refresh token or re-authenticate
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Retry request
except GagiteckError as e:
    print(f"API error: {e.message} (code: {e.code})")
    # Log and handle gracefully
```

### Retry Logic

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        delay = e.retry_after or (base_delay * 2 ** attempt)
                        time.sleep(delay)
                    else:
                        raise
                except GagiteckError as e:
                    if e.status >= 500 and attempt < max_retries - 1:
                        time.sleep(base_delay * 2 ** attempt)
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def run_agent(client, agent_id, message):
    return client.agents.run(agent_id, message=message)
```

---

## Rate Limiting

### Understanding Limits

| Plan | Requests/Min | Tokens/Min |
|------|--------------|------------|
| Free | 100 | 100,000 |
| Pro | 1,000 | 1,000,000 |
| Enterprise | Custom | Custom |

### Handling Rate Limits

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()

    def acquire(self):
        now = time.time()

        # Remove old requests
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()

        if len(self.requests) >= self.max_requests:
            # Wait for oldest request to expire
            sleep_time = self.requests[0] + self.window_seconds - now
            time.sleep(sleep_time)
            self.requests.popleft()

        self.requests.append(now)

# Usage
limiter = RateLimiter(max_requests=100, window_seconds=60)

for message in messages:
    limiter.acquire()
    response = client.agents.run(agent_id, message=message)
```

---

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch

def test_agent_run():
    mock_client = Mock()
    mock_client.agents.run.return_value = Mock(
        content="Hello! I'm here to help.",
        usage={"input_tokens": 10, "output_tokens": 20}
    )

    result = mock_client.agents.run("agent_123", message="Hello")

    assert "Hello" in result.content
    mock_client.agents.run.assert_called_once_with(
        "agent_123",
        message="Hello"
    )
```

### Integration Testing

```python
import pytest

@pytest.fixture
def test_client():
    return Gagiteck(api_key=os.environ["GAGITECK_TEST_API_KEY"])

@pytest.fixture
def test_agent(test_client):
    agent = test_client.agents.create(
        name="Test Agent",
        system_prompt="Reply with 'test successful'"
    )
    yield agent
    # Cleanup
    test_client.agents.delete(agent.id)

def test_agent_responds(test_client, test_agent):
    response = test_client.agents.run(
        test_agent.id,
        message="Run test"
    )

    assert "test successful" in response.content.lower()
```

### End-to-End Testing

```python
def test_full_workflow(test_client):
    # Create agents
    classifier = test_client.agents.create(
        name="E2E Classifier",
        system_prompt="Classify as positive or negative"
    )

    # Create workflow
    workflow = test_client.workflows.create(
        name="E2E Workflow",
        steps=[
            {"type": "agent", "config": {"agent_id": classifier.id}}
        ]
    )

    # Trigger and wait
    execution = test_client.workflows.trigger(
        workflow.id,
        input={"text": "This is great!"}
    )

    # Poll for completion
    for _ in range(30):
        execution = test_client.executions.get(execution.id)
        if execution.status != "running":
            break
        time.sleep(1)

    assert execution.status == "completed"
    assert "positive" in execution.result.lower()

    # Cleanup
    test_client.workflows.delete(workflow.id)
    test_client.agents.delete(classifier.id)
```

---

## Deployment

### Environment Configuration

```bash
# .env.production
GAGITECK_API_KEY=ggt_live_xxx
GAGITECK_WEBHOOK_SECRET=whsec_xxx
GAGITECK_API_URL=https://api.mimoai.co
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GAGITECK_API_KEY=""

CMD ["python", "main.py"]
```

### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gagiteck-secrets
type: Opaque
stringData:
  api-key: ggt_live_xxx
  webhook-secret: whsec_xxx
```

### Health Checks

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    try:
        # Test API connection
        client.health()
        return jsonify({"status": "healthy", "gagiteck": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
```

---

## Support

- **API Status**: [status.mimoai.co](https://status.mimoai.co)
- **Discord**: [discord.gg/gagiteck](https://discord.gg/gagiteck)
- **Email**: developers@gagiteck.com
- **GitHub Issues**: [github.com/ajaniethos-1/gagiteck-python](https://github.com/ajaniethos-1/gagiteck-python/issues)
