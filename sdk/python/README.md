# Gagiteck Python SDK

[![PyPI version](https://badge.fury.io/py/gagiteck.svg)](https://pypi.org/project/gagiteck/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python client library for the Gagiteck AI SaaS Platform.

## Installation

```bash
pip install gagiteck
```

## Quick Start

### Using the API Client

```python
from gagiteck import Client

# Initialize the client
client = Client(api_key="ggt_your_api_key")

# List agents
agents = client.agents.list()
print(f"Found {len(agents['data'])} agents")

# Create an agent
agent = client.agents.create(
    name="My Assistant",
    system_prompt="You are a helpful assistant.",
    config={"model": "claude-3-sonnet"}
)
print(f"Created agent: {agent['id']}")

# Run an agent
response = client.agents.run(
    agent_id=agent["id"],
    message="Hello, how can you help me?"
)
print(response["content"])
```

### Creating Agents Locally

```python
from gagiteck import Agent, tool

# Define a custom tool
@tool
def search_database(query: str) -> str:
    """Search the database for information."""
    # Your search logic here
    return f"Results for: {query}"

# Create an agent with tools
agent = Agent(
    name="Research Assistant",
    model="claude-3-opus",
    tools=[search_database],
    system_prompt="You are a helpful research assistant.",
    memory_enabled=True,
)

# Run the agent
response = agent.run("Find information about AI agents")
print(response.text)

# Continue the conversation (memory enabled)
response = agent.run("Tell me more about the first result")
print(response.text)
```

### Working with Workflows

```python
from gagiteck import Client

client = Client(api_key="ggt_your_api_key")

# Create a workflow
workflow = client.workflows.create(
    name="Customer Onboarding",
    steps=[
        {"id": "verify", "name": "Verify Email", "agent_id": "agent_verifier"},
        {"id": "setup", "name": "Setup Account", "agent_id": "agent_provisioner", "depends_on": ["verify"]},
        {"id": "welcome", "name": "Send Welcome", "agent_id": "agent_messenger", "depends_on": ["setup"]},
    ]
)

# Trigger the workflow
run = client.workflows.trigger(
    workflow_id=workflow["id"],
    inputs={"user_email": "user@example.com"}
)
print(f"Workflow run started: {run['id']}")
```

## Features

- **Simple API Client** - Easy-to-use client for the Gagiteck REST API
- **Local Agents** - Create and run agents locally with memory support
- **Custom Tools** - Define tools using the `@tool` decorator
- **Type Safe** - Full type annotations for IDE support
- **Async Support** - Async client available (coming soon)

## API Reference

### Client

```python
Client(
    api_key: str,           # Your API key (starts with 'ggt_')
    base_url: str = None,   # Custom API URL
    timeout: int = 30,      # Request timeout in seconds
    debug: bool = False,    # Enable debug logging
)
```

### Agent

```python
Agent(
    name: str,                      # Agent name
    model: str = "claude-3-sonnet", # LLM model
    system_prompt: str = None,      # System instructions
    tools: list = [],               # List of tools
    memory_enabled: bool = False,   # Enable conversation memory
    max_tokens: int = 4096,         # Max response tokens
    temperature: float = 0.7,       # Sampling temperature
)
```

### Tool Decorator

```python
@tool
def my_function(param: str) -> str:
    """Description of what the tool does."""
    return result
```

## Error Handling

```python
from gagiteck import Client, GagiteckError, AuthenticationError, APIError

try:
    client = Client(api_key="ggt_your_key")
    response = client.agents.run(agent_id="agent_123", message="Hello")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error {e.code}: {e.message}")
except GagiteckError as e:
    print(f"Error: {e.message}")
```

## Development

```bash
# Clone the repository
git clone https://github.com/ajaniethos-1/gagiteck-python.git
cd gagiteck-python

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests -v

# Run linting
ruff check gagiteck tests

# Run type checking
mypy gagiteck
```

## Documentation

- [Full Documentation](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/docs)
- [API Reference](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/docs/api-reference.md)
- [Examples](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/examples)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ajaniethos-1/gagiteck-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/discussions)
- **Email**: support@gagiteck.com
