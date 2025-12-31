# Troubleshooting Guide

Solutions to common issues with the Gagiteck AI SaaS Platform.

---

## Installation Issues

### Docker won't start

**Symptom**: `docker-compose up` fails or containers won't start.

**Solutions**:

1. Check Docker is running:
   ```bash
   docker info
   ```

2. Free up resources:
   ```bash
   docker system prune -a
   ```

3. Check port conflicts:
   ```bash
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

4. Increase Docker memory (Docker Desktop → Settings → Resources)

### Database connection failed

**Symptom**: `Error: connect ECONNREFUSED 127.0.0.1:5432`

**Solutions**:

1. Verify PostgreSQL is running:
   ```bash
   docker-compose ps db
   # or
   sudo systemctl status postgresql
   ```

2. Check connection string:
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:password@localhost:5432/gagiteck
   ```

3. Test connection:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

4. Check firewall rules allowing port 5432

### Redis connection failed

**Symptom**: `Error: Redis connection to localhost:6379 failed`

**Solutions**:

1. Verify Redis is running:
   ```bash
   docker-compose ps redis
   # or
   redis-cli ping
   ```

2. Check Redis URL:
   ```bash
   echo $REDIS_URL
   ```

3. Test connection:
   ```bash
   redis-cli -u $REDIS_URL ping
   ```

---

## Authentication Issues

### API key not working

**Symptom**: `401 Unauthorized` or `Invalid API key`

**Solutions**:

1. Verify key format (should start with `ggt_`):
   ```bash
   echo $GAGITECK_API_KEY
   ```

2. Check key hasn't expired:
   ```python
   keys = client.api_keys.list()
   for key in keys:
       print(f"{key.name}: expires {key.expires_at}")
   ```

3. Verify key has required scopes:
   ```python
   key_info = client.api_keys.get(key_id="key_123")
   print(key_info.scopes)
   ```

4. Regenerate if compromised:
   ```python
   client.api_keys.revoke(key_id="key_123")
   new_key = client.api_keys.create(name="New Key", scopes=["agents:run"])
   ```

### JWT token expired

**Symptom**: `401 Token expired`

**Solution**:

```python
from gagiteck import Client

# Refresh the token
client = Client(token=expired_token)
new_tokens = client.auth.refresh(refresh_token)

# Use new access token
client = Client(token=new_tokens.access_token)
```

### OAuth callback failing

**Symptom**: OAuth flow doesn't complete, callback errors

**Solutions**:

1. Verify redirect URI matches exactly:
   ```python
   # Must match what's registered with the OAuth provider
   auth_url = client.integrations.connect(
       provider="slack",
       redirect_uri="https://yourapp.com/oauth/callback"  # Exact match!
   )
   ```

2. Check state parameter:
   ```python
   # State should match what you sent
   tokens = client.integrations.complete_oauth(
       provider="slack",
       code=request.query.code,
       state=request.query.state  # Verify this matches
   )
   ```

---

## Agent Issues

### Agent not responding

**Symptom**: Agent execution hangs or times out

**Solutions**:

1. Check agent status:
   ```python
   agent = client.agents.get(agent_id="agent_123")
   print(f"Status: {agent.status}")
   ```

2. Verify LLM provider is available:
   ```bash
   curl https://api.anthropic.com/v1/messages -I
   curl https://api.openai.com/v1/chat/completions -I
   ```

3. Check API keys for LLM providers:
   ```bash
   echo $ANTHROPIC_API_KEY
   echo $OPENAI_API_KEY
   ```

4. Reduce complexity:
   ```python
   # Try simpler configuration
   agent = client.agents.create(
       name="Test Agent",
       model="claude-3-haiku",  # Faster model
       max_tokens=500,          # Lower limit
       timeout_ms=30000         # Shorter timeout
   )
   ```

### Slow agent responses

**Symptom**: Responses take 10+ seconds

**Solutions**:

1. Use a faster model:
   ```python
   # Haiku is fastest, Opus is slowest
   agent = client.agents.update(
       agent_id="agent_123",
       model="claude-3-haiku"
   )
   ```

2. Reduce max_tokens:
   ```python
   agent = client.agents.update(
       agent_id="agent_123",
       max_tokens=1000  # Lower = faster
   )
   ```

3. Simplify system prompt:
   ```python
   # Shorter prompts = faster processing
   agent = client.agents.update(
       agent_id="agent_123",
       system_prompt="You are a helpful assistant. Be concise."
   )
   ```

4. Enable streaming:
   ```python
   # Get first tokens faster
   for chunk in client.agents.run_stream(agent_id="agent_123", message="Hello"):
       print(chunk.content, end="")
   ```

### Tool calls failing

**Symptom**: `Tool execution failed` or tool returns errors

**Solutions**:

1. Check tool permissions:
   ```python
   agent = client.agents.get(agent_id="agent_123")
   print(agent.tool_permissions)
   ```

2. Test tool in isolation:
   ```python
   # Run tool directly
   result = client.tools.test(
       tool_name="web_search",
       input={"query": "test"}
   )
   print(result)
   ```

3. Check external service status:
   ```python
   # For integrations
   status = client.integrations.test(connection_id="conn_123")
   print(f"Connected: {status.connected}")
   print(f"Error: {status.error}")
   ```

4. Review tool logs:
   ```python
   execution = client.executions.get(execution_id="exec_123")
   for tool_call in execution.tool_calls:
       print(f"Tool: {tool_call.tool}")
       print(f"Input: {tool_call.input}")
       print(f"Output: {tool_call.output}")
       print(f"Error: {tool_call.error}")
   ```

### Agent giving wrong answers

**Symptom**: Agent responses are incorrect or off-topic

**Solutions**:

1. Improve system prompt:
   ```python
   # Be more specific
   system_prompt = """You are a customer support agent for Acme Corp.

   IMPORTANT RULES:
   - Only answer questions about Acme products
   - If unsure, say "I don't know" and offer to connect to a human
   - Never make up information
   - Always be polite and professional

   AVAILABLE PRODUCTS:
   - Widget Pro ($99)
   - Widget Basic ($49)
   - Widget Enterprise (contact sales)
   """
   ```

2. Add examples (few-shot):
   ```python
   system_prompt = """...

   EXAMPLES:
   User: "What's the price of Widget Pro?"
   You: "Widget Pro is $99. Would you like me to help you with a purchase?"

   User: "Do you sell cars?"
   You: "I apologize, but Acme Corp only sells Widget products. Is there anything about our widgets I can help you with?"
   """
   ```

3. Use RAG for knowledge:
   ```python
   # Connect to knowledge base
   agent = client.agents.create(
       name="Knowledgeable Agent",
       memory_type="rag",
       knowledge_base_id="kb_123"
   )
   ```

---

## Workflow Issues

### Workflow stuck

**Symptom**: Workflow run shows "running" but doesn't progress

**Solutions**:

1. Check run status:
   ```python
   run = client.workflows.get_run(run_id="run_123")
   for step in run.steps:
       print(f"{step.id}: {step.status}")
       if step.error:
           print(f"  Error: {step.error}")
   ```

2. Check for dependency deadlocks:
   ```yaml
   # BAD: Circular dependency
   steps:
     - id: a
       depends_on: [c]  # Deadlock!
     - id: b
       depends_on: [a]
     - id: c
       depends_on: [b]
   ```

3. Cancel stuck run:
   ```python
   client.workflows.cancel(run_id="run_123")
   ```

### Step outputs not passing correctly

**Symptom**: `undefined` or empty values in step inputs

**Solutions**:

1. Check variable syntax:
   ```yaml
   # Correct
   input: "Data: {{steps.previous_step.output}}"

   # Wrong
   input: "Data: {steps.previous_step.output}"
   input: "Data: {{ steps.previous_step.output }}"  # No spaces!
   ```

2. Verify dependency:
   ```yaml
   - id: step2
     input: "{{steps.step1.output}}"
     depends_on: [step1]  # Must include step1!
   ```

3. Check output format:
   ```python
   # If previous step returns JSON
   input: "{{steps.previous.output | json}}"

   # Access nested properties
   input: "{{steps.previous.output.data.value}}"
   ```

---

## Performance Issues

### High memory usage

**Solutions**:

1. Reduce memory window:
   ```python
   agent = client.agents.update(
       agent_id="agent_123",
       memory_window=10  # Keep fewer messages
   )
   ```

2. Clear old conversations:
   ```python
   client.conversations.delete(conversation_id="conv_123")
   ```

3. Use streaming for large responses:
   ```python
   for chunk in client.agents.run_stream(...):
       process(chunk)
   ```

### High latency

**Solutions**:

1. Check region - use closest:
   ```python
   client = Client(
       api_key="YOUR_KEY",
       base_url="https://api-eu.gagiteck.com"  # EU endpoint
   )
   ```

2. Enable connection pooling:
   ```python
   client = Client(
       api_key="YOUR_KEY",
       pool_size=10
   )
   ```

3. Use batch operations:
   ```python
   # Instead of multiple calls
   results = client.agents.run_batch([
       {"agent_id": "a", "message": "m1"},
       {"agent_id": "b", "message": "m2"},
   ])
   ```

---

## Getting Help

### Check Status Page

[status.gagiteck.com](https://status.gagiteck.com)

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = Client(api_key="YOUR_KEY", debug=True)
```

### Contact Support

- **Email**: support@gagiteck.com
- **GitHub Issues**: [Report a bug](https://github.com/gagiteck/gagiteck-assets/issues)
- **Discussions**: [Ask questions](https://github.com/gagiteck/gagiteck-assets/discussions)
