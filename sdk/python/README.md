# Gagiteck Python SDK

Official Python client library for the Gagiteck AI SaaS Platform.

## Installation

```bash
pip install gagiteck
```

## Quick Start

```python
from gagiteck import Client

# Initialize the client
client = Client(api_key="ggt_your_api_key")

# List agents
agents = client.agents.list()

# Run an agent
response = client.agents.run(
    agent_id="agent_123",
    message="Hello, how can you help me?"
)
print(response)
```

## Creating Agents Locally

```python
from gagiteck import Agent, tool

# Define a custom tool
@tool
def search_database(query: str) -> str:
    """Search the database for information."""
    return f"Results for: {query}"

# Create an agent
agent = Agent(
    name="Research Assistant",
    model="claude-3-opus",
    tools=[search_database],
    system_prompt="You are a helpful research assistant."
)

# Run the agent
response = agent.run("Find information about AI")
print(response.text)
```

## Features

- **Simple API Client** - Easy-to-use client for the Gagiteck REST API
- **Local Agents** - Create and run agents locally
- **Custom Tools** - Define tools using the `@tool` decorator
- **Type Safe** - Full type annotations for IDE support
- **Async Support** - Coming soon

## Documentation

See the [full documentation](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/docs) for more details.

## License

MIT License - see [LICENSE](LICENSE) for details.
