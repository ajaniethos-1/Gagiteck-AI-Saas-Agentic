# Python SDK Guide

Official Python client library for the Gagiteck AI SaaS Platform.

## Installation

```bash
pip install gagiteck
```

Or install with optional dependencies:

```bash
# With async support
pip install gagiteck[async]

# With all extras
pip install gagiteck[all]
```

## Quick Start

### API Client

```python
from gagiteck import Client

# Initialize the client
client = Client(api_key="ggt_your_api_key")

# List all agents
agents = client.agents.list()
for agent in agents["data"]:
    print(f"  - {agent['name']} ({agent['id']})")

# Create an agent
agent = client.agents.create(
    name="Customer Support Bot",
    system_prompt="You are a helpful customer support agent.",
    config={"model": "claude-3-sonnet"}
)

# Run an agent
response = client.agents.run(
    agent_id=agent["id"],
    message="How do I reset my password?"
)
print(response["content"])
```

### Local Agents

```python
from gagiteck import Agent, tool

# Define custom tools
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for answers."""
    # Implementation here
    return f"Found answer for: {query}"

@tool
def create_ticket(subject: str, description: str) -> dict:
    """Create a support ticket."""
    return {"ticket_id": "TKT-001", "status": "created"}

# Create an agent with tools
agent = Agent(
    name="Support Agent",
    model="claude-3-opus",
    system_prompt="You are a customer support agent.",
    tools=[search_knowledge_base, create_ticket],
    memory_enabled=True,
)

# Run the agent
response = agent.run("I need help with billing")
print(response.text)
```

## Client Configuration

```python
from gagiteck import Client

client = Client(
    api_key="ggt_your_api_key",      # Required: API key
    base_url="https://api.custom.com", # Optional: Custom API URL
    timeout=60,                        # Optional: Request timeout (default: 30)
    max_retries=3,                     # Optional: Retry count (default: 3)
    debug=True,                        # Optional: Enable debug logging
)
```

### Environment Variables

```bash
export GAGITECK_API_KEY="ggt_your_api_key"
export GAGITECK_BASE_URL="https://api.gagiteck.com"
```

```python
from gagiteck import Client

# Client will automatically use environment variables
client = Client()
```

## Agents API

### List Agents

```python
# List all agents
agents = client.agents.list()

# With pagination
agents = client.agents.list(limit=10, offset=0)

# Filter by status
agents = client.agents.list(status="active")
```

### Create Agent

```python
agent = client.agents.create(
    name="Research Assistant",
    system_prompt="You are a research assistant.",
    config={
        "model": "claude-3-sonnet",
        "max_tokens": 4096,
        "temperature": 0.7,
    },
    tools=["web_search", "document_reader"],
    metadata={"department": "research"}
)
```

### Get Agent

```python
agent = client.agents.get(agent_id="agent_123")
print(f"Name: {agent['name']}")
print(f"Status: {agent['status']}")
```

### Update Agent

```python
agent = client.agents.update(
    agent_id="agent_123",
    name="Updated Name",
    config={"temperature": 0.5}
)
```

### Delete Agent

```python
client.agents.delete(agent_id="agent_123")
```

### Run Agent

```python
# Simple run
response = client.agents.run(
    agent_id="agent_123",
    message="Hello, how can you help?"
)

# With conversation context
response = client.agents.run(
    agent_id="agent_123",
    message="Tell me more",
    conversation_id="conv_456"
)

# With streaming
for chunk in client.agents.run_stream(
    agent_id="agent_123",
    message="Write a long story"
):
    print(chunk["content"], end="", flush=True)
```

## Workflows API

### Create Workflow

```python
workflow = client.workflows.create(
    name="Data Processing Pipeline",
    description="Process and analyze data",
    steps=[
        {
            "id": "extract",
            "name": "Extract Data",
            "agent_id": "agent_extractor"
        },
        {
            "id": "transform",
            "name": "Transform Data",
            "agent_id": "agent_transformer",
            "depends_on": ["extract"]
        },
        {
            "id": "load",
            "name": "Load Data",
            "agent_id": "agent_loader",
            "depends_on": ["transform"]
        }
    ]
)
```

### Trigger Workflow

```python
run = client.workflows.trigger(
    workflow_id="wf_123",
    inputs={
        "source": "database",
        "destination": "warehouse"
    }
)
print(f"Run ID: {run['id']}")
print(f"Status: {run['status']}")
```

### Get Workflow Run

```python
run = client.workflows.get_run(
    workflow_id="wf_123",
    run_id="run_456"
)

for step in run["steps"]:
    print(f"  {step['name']}: {step['status']}")
```

## Async Client

```python
import asyncio
from gagiteck import AsyncClient

async def main():
    client = AsyncClient(api_key="ggt_your_api_key")

    # Async agent operations
    agents = await client.agents.list()

    # Run agent asynchronously
    response = await client.agents.run(
        agent_id="agent_123",
        message="Hello!"
    )

    # Parallel execution
    tasks = [
        client.agents.run(agent_id="agent_1", message="Task 1"),
        client.agents.run(agent_id="agent_2", message="Task 2"),
        client.agents.run(agent_id="agent_3", message="Task 3"),
    ]
    results = await asyncio.gather(*tasks)

    await client.close()

asyncio.run(main())
```

## Custom Tools

### Basic Tool

```python
from gagiteck import tool

@tool
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

### Tool with Complex Types

```python
from gagiteck import tool
from typing import List, Dict

@tool
def search_products(
    query: str,
    category: str = None,
    limit: int = 10
) -> List[Dict]:
    """Search for products in the catalog.

    Args:
        query: Search query string
        category: Optional category filter
        limit: Maximum results to return
    """
    # Implementation
    return [{"name": "Product", "price": 99.99}]
```

### Async Tools

```python
from gagiteck import async_tool
import httpx

@async_tool
async def fetch_weather(city: str) -> dict:
    """Fetch current weather for a city."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/current/{city}"
        )
        return response.json()
```

## Error Handling

```python
from gagiteck import (
    Client,
    GagiteckError,
    AuthenticationError,
    RateLimitError,
    APIError,
    ValidationError,
)

client = Client(api_key="ggt_your_key")

try:
    response = client.agents.run(
        agent_id="agent_123",
        message="Hello"
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.details}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
except GagiteckError as e:
    print(f"Unexpected error: {e}")
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gagiteck")
logger.setLevel(logging.DEBUG)

# Or use client debug mode
client = Client(api_key="ggt_key", debug=True)
```

## Type Hints

The SDK is fully typed for IDE support:

```python
from gagiteck import Client
from gagiteck.types import Agent, AgentConfig, Workflow

client = Client(api_key="ggt_key")

# IDE will show type hints
agent: Agent = client.agents.get("agent_123")
config: AgentConfig = agent["config"]
```

## Examples

### Chatbot with Memory

```python
from gagiteck import Agent

agent = Agent(
    name="Chatbot",
    model="claude-3-sonnet",
    memory_enabled=True,
    system_prompt="You are a friendly chatbot."
)

# Multi-turn conversation
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break

    response = agent.run(user_input)
    print(f"Bot: {response.text}")
```

### RAG Agent

```python
from gagiteck import Agent, tool
import chromadb

# Setup vector store
chroma = chromadb.Client()
collection = chroma.create_collection("docs")

@tool
def search_documents(query: str) -> list:
    """Search documents for relevant information."""
    results = collection.query(query_texts=[query], n_results=5)
    return results["documents"][0]

agent = Agent(
    name="RAG Agent",
    model="claude-3-opus",
    tools=[search_documents],
    system_prompt="""You are a helpful assistant.
    Use the search_documents tool to find information."""
)

response = agent.run("What is our refund policy?")
print(response.text)
```

## Best Practices

1. **Use Environment Variables**: Store API keys in environment variables
2. **Handle Errors**: Always wrap API calls in try/except
3. **Use Async**: For high-throughput applications, use AsyncClient
4. **Enable Memory**: Use memory_enabled for conversational agents
5. **Type Your Tools**: Add type hints and docstrings to tools

## Resources

- [API Reference](api-reference.md)
- [GitHub Repository](https://github.com/ajaniethos-1/gagiteck-python)
- [PyPI Package](https://pypi.org/project/gagiteck/)
- [Examples](https://github.com/ajaniethos-1/Gagiteck-AI-Saas-Agentic/tree/main/examples)
