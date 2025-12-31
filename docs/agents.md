# AI Agents Guide

This guide covers everything you need to know about creating and managing AI agents in Gagiteck.

## What is an Agent?

An **Agent** is an autonomous AI entity that can:
- Understand natural language instructions
- Reason about complex problems
- Use tools to interact with external systems
- Maintain conversation context
- Execute multi-step tasks

---

## Creating Agents

### Basic Agent

```python
from gagiteck import Client

client = Client(api_key="YOUR_API_KEY")

agent = client.agents.create(
    name="Customer Support Agent",
    model="claude-3-opus",
    system_prompt="""You are a helpful customer support agent for Acme Corp.
    You help customers with:
    - Order inquiries
    - Product questions
    - Returns and refunds

    Be friendly, professional, and concise."""
)
```

### Agent with Tools

```python
from gagiteck import Client, tool

@tool
def lookup_order(order_id: str) -> dict:
    """Look up order details by order ID."""
    return database.get_order(order_id)

@tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund for an order."""
    return payments.refund(order_id, reason)

agent = client.agents.create(
    name="Support Agent with Tools",
    model="claude-3-opus",
    tools=[lookup_order, process_refund],
    system_prompt="You are a customer support agent with access to order and refund systems."
)
```

---

## Agent Configuration

### Full Configuration Options

```python
agent = client.agents.create(
    # Basic Info
    name="Advanced Agent",
    description="An advanced agent with full configuration",

    # Model Settings
    model="claude-3-opus",
    temperature=0.7,
    max_tokens=4096,

    # System Prompt
    system_prompt="You are a helpful assistant.",

    # Tools
    tools=[tool1, tool2, tool3],

    # Memory
    memory_enabled=True,
    memory_type="conversation",  # or "long_term", "rag"
    memory_window=20,  # Number of messages to retain

    # Behavior
    stop_sequences=["Human:", "END"],
    response_format="text",  # or "json", "markdown"

    # Safety
    content_filter=True,
    allowed_domains=["api.example.com"],

    # Metadata
    tags=["production", "customer-support"],
    metadata={"team": "support", "version": "1.0"}
)
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Unique agent name |
| `model` | string | LLM model identifier |
| `system_prompt` | string | Instructions for the agent |
| `temperature` | float | Creativity (0.0-2.0) |
| `max_tokens` | int | Max response length |
| `tools` | list | Available tools |
| `memory_enabled` | bool | Enable conversation memory |
| `memory_type` | string | Type of memory system |

---

## Running Agents

### Single Message

```python
response = client.agents.run(
    agent_id="agent_123",
    message="What's the status of order #12345?"
)

print(response.content)
```

### Conversation (Multi-turn)

```python
# Start a conversation
conversation = client.conversations.create(agent_id="agent_123")

# First message
response1 = client.conversations.send(
    conversation_id=conversation.id,
    message="Hi, I need help with my order"
)

# Follow-up (context is maintained)
response2 = client.conversations.send(
    conversation_id=conversation.id,
    message="The order number is #12345"
)

# Agent remembers the context
response3 = client.conversations.send(
    conversation_id=conversation.id,
    message="Can you check if it shipped?"
)
```

### Streaming Responses

```python
# Stream response tokens
for chunk in client.agents.run_stream(
    agent_id="agent_123",
    message="Write a long blog post about AI"
):
    print(chunk.content, end="", flush=True)
```

---

## Tools

### Defining Tools

Tools are Python functions decorated with `@tool`:

```python
from gagiteck import tool

@tool
def search_database(
    query: str,
    limit: int = 10,
    filters: dict = None
) -> list:
    """
    Search the database for matching records.

    Args:
        query: Search query string
        limit: Maximum number of results
        filters: Optional filters to apply

    Returns:
        List of matching records
    """
    return db.search(query, limit=limit, filters=filters)
```

### Tool Schema

The decorator automatically generates a JSON schema:

```json
{
  "name": "search_database",
  "description": "Search the database for matching records.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query string"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results",
        "default": 10
      },
      "filters": {
        "type": "object",
        "description": "Optional filters to apply"
      }
    },
    "required": ["query"]
  }
}
```

### Built-in Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `web_search` | Search the web | Research, fact-checking |
| `read_file` | Read file contents | Document processing |
| `write_file` | Write to files | Content generation |
| `run_python` | Execute Python code | Calculations, analysis |
| `http_request` | Make HTTP calls | API integrations |
| `send_email` | Send emails | Notifications |
| `sql_query` | Run SQL queries | Database access |

---

## Memory Systems

### Conversation Memory

Short-term memory within a conversation:

```python
agent = client.agents.create(
    name="Conversational Agent",
    memory_enabled=True,
    memory_type="conversation",
    memory_window=20  # Remember last 20 messages
)
```

### Long-term Memory

Persistent memory across conversations:

```python
agent = client.agents.create(
    name="Personal Assistant",
    memory_enabled=True,
    memory_type="long_term",
    memory_config={
        "store": "vector_db",
        "retrieval_count": 5,
        "relevance_threshold": 0.7
    }
)
```

### RAG (Retrieval-Augmented Generation)

Connect agents to knowledge bases:

```python
# Create a knowledge base
kb = client.knowledge_bases.create(
    name="Product Documentation",
    documents=["docs/manual.pdf", "docs/faq.md"]
)

# Attach to agent
agent = client.agents.create(
    name="Documentation Agent",
    memory_type="rag",
    knowledge_base_id=kb.id
)
```

---

## Agent Patterns

### Specialist Agent

Focused on one domain:

```python
sql_expert = client.agents.create(
    name="SQL Expert",
    model="claude-3-opus",
    system_prompt="""You are an expert SQL developer.
    You help users write, optimize, and debug SQL queries.
    Always explain your queries and suggest optimizations.""",
    tools=[sql_query, explain_query]
)
```

### Router Agent

Delegates to specialist agents:

```python
router = client.agents.create(
    name="Router Agent",
    system_prompt="""You are a routing agent.
    Analyze the user's request and delegate to the appropriate specialist:
    - SQL questions → sql_expert
    - Python questions → python_expert
    - General questions → answer directly""",
    tools=[delegate_to_agent]
)
```

### Autonomous Agent

Self-directed task completion:

```python
researcher = client.agents.create(
    name="Research Agent",
    system_prompt="""You are an autonomous research agent.
    Given a topic, you will:
    1. Search for relevant information
    2. Analyze and synthesize findings
    3. Generate a comprehensive report

    Work step by step until the task is complete.""",
    tools=[web_search, read_file, write_file],
    autonomous_mode=True,
    max_iterations=10
)
```

---

## Best Practices

### 1. Clear System Prompts

```python
# Good: Specific and structured
system_prompt = """You are a customer support agent for TechCorp.

## Your Role
- Help customers with product questions
- Process returns and refunds
- Escalate complex issues

## Guidelines
- Be friendly and professional
- Ask clarifying questions when needed
- Never share internal system details

## Available Tools
- lookup_order: Get order details
- process_refund: Issue refunds (requires manager approval for >$100)
"""

# Bad: Vague
system_prompt = "You are a helpful assistant."
```

### 2. Tool Documentation

```python
# Good: Detailed docstring
@tool
def get_customer(customer_id: str) -> dict:
    """
    Retrieve customer information by ID.

    Use this tool when you need to look up customer details
    such as name, email, order history, or account status.

    Args:
        customer_id: The unique customer identifier (format: CUST-XXXXX)

    Returns:
        Customer object with fields: id, name, email, orders, status

    Raises:
        NotFoundError: If customer doesn't exist
    """
    return customers.get(customer_id)
```

### 3. Error Handling

```python
@tool
def risky_operation(data: dict) -> str:
    """Perform an operation that might fail."""
    try:
        result = external_api.call(data)
        return f"Success: {result}"
    except ExternalAPIError as e:
        return f"Error: {e.message}. Please try again or contact support."
```

---

## Monitoring & Debugging

### View Execution Logs

```python
# Get agent execution history
history = client.agents.get_executions(
    agent_id="agent_123",
    limit=10
)

for execution in history:
    print(f"ID: {execution.id}")
    print(f"Status: {execution.status}")
    print(f"Duration: {execution.duration_ms}ms")
    print(f"Tokens: {execution.tokens_used}")
    print(f"Tool Calls: {len(execution.tool_calls)}")
```

### Debug Mode

```python
response = client.agents.run(
    agent_id="agent_123",
    message="Debug this issue",
    debug=True
)

# Access debug info
print(response.debug.prompt_tokens)
print(response.debug.completion_tokens)
print(response.debug.tool_calls)
print(response.debug.reasoning_trace)
```

---

## Related Documentation

- [Workflows Guide](workflows.md)
- [Tools & Integrations](integrations.md)
- [API Reference](api-reference.md)
