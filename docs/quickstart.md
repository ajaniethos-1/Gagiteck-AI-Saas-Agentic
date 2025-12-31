# Quick Start Guide

Build your first AI agent in 5 minutes.

## Prerequisites

- Gagiteck platform installed and running
- API key configured in `.env`

---

## Step 1: Create Your First Agent

### Using the Web UI

1. Navigate to http://localhost:3000
2. Click **"New Agent"** in the dashboard
3. Configure your agent:
   - **Name**: `My First Agent`
   - **Model**: `claude-3-opus` or `gpt-4`
   - **System Prompt**: `You are a helpful assistant that answers questions clearly and concisely.`
4. Click **"Create Agent"**

### Using the API

```bash
curl -X POST http://localhost:8000/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Agent",
    "model": "claude-3-opus",
    "system_prompt": "You are a helpful assistant."
  }'
```

### Using Python SDK

```python
from gagiteck import Client

client = Client(api_key="YOUR_API_KEY")

agent = client.agents.create(
    name="My First Agent",
    model="claude-3-opus",
    system_prompt="You are a helpful assistant."
)

print(f"Created agent: {agent.id}")
```

---

## Step 2: Run Your Agent

### Web UI
1. Select your agent from the dashboard
2. Type a message in the chat interface
3. Press Enter or click Send

### API

```bash
curl -X POST http://localhost:8000/v1/agents/AGENT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?"
  }'
```

### Python SDK

```python
response = client.agents.run(
    agent_id=agent.id,
    message="What is the capital of France?"
)

print(response.content)
# Output: The capital of France is Paris.
```

---

## Step 3: Add Tools to Your Agent

Tools give your agent capabilities beyond conversation.

### Define a Custom Tool

```python
from gagiteck import Client, tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Your implementation here
    return f"The weather in {city} is sunny and 72°F"

# Create agent with tool
agent = client.agents.create(
    name="Weather Assistant",
    model="claude-3-opus",
    tools=[get_weather],
    system_prompt="You help users check the weather."
)

# The agent can now use the tool
response = client.agents.run(
    agent_id=agent.id,
    message="What's the weather in San Francisco?"
)
```

### Built-in Tools

Gagiteck includes pre-built tools:

| Tool | Description |
|------|-------------|
| `web_search` | Search the internet |
| `read_file` | Read local files |
| `write_file` | Write to files |
| `run_code` | Execute Python code |
| `send_email` | Send emails via SMTP |
| `http_request` | Make HTTP API calls |

```python
from gagiteck.tools import web_search, read_file

agent = client.agents.create(
    name="Research Agent",
    model="claude-3-opus",
    tools=[web_search, read_file]
)
```

---

## Step 4: Create a Workflow

Workflows chain multiple agents together.

### Define a Workflow

```yaml
# workflows/research-pipeline.yaml
name: Research Pipeline
description: Research a topic and generate a summary

steps:
  - name: research
    agent: research-agent
    input: "Research the topic: {{topic}}"

  - name: summarize
    agent: summarizer-agent
    input: "Summarize this research: {{steps.research.output}}"
    depends_on: research

  - name: format
    agent: formatter-agent
    input: "Format as a blog post: {{steps.summarize.output}}"
    depends_on: summarize

output: "{{steps.format.output}}"
```

### Trigger the Workflow

```python
result = client.workflows.run(
    workflow_id="research-pipeline",
    inputs={"topic": "Artificial Intelligence trends in 2025"}
)

print(result.output)
```

---

## Step 5: Monitor & Debug

### View Agent Logs

```python
# Get execution history
history = client.agents.get_history(agent_id=agent.id)

for execution in history:
    print(f"{execution.timestamp}: {execution.status}")
    print(f"  Input: {execution.input}")
    print(f"  Output: {execution.output}")
```

### Dashboard Metrics

The web dashboard at `/dashboard` shows:
- Total executions
- Success/error rates
- Average response time
- Token usage
- Cost tracking

---

## Next Steps

- [Agents Deep Dive](agents.md) - Advanced agent configuration
- [Workflows Guide](workflows.md) - Complex automation patterns
- [API Reference](api-reference.md) - Complete API documentation
- [Integrations](integrations.md) - Connect external services
