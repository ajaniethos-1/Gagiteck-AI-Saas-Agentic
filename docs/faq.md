# Frequently Asked Questions

Common questions and answers about the Gagiteck AI SaaS Platform.

---

## General

### What is Gagiteck?

Gagiteck is an AI SaaS platform that enables businesses to build, deploy, and manage autonomous AI agents. These agents can automate complex workflows, integrate with existing tools, and handle tasks that traditionally required human intervention.

### What can I build with Gagiteck?

- **Customer Support Agents** - Handle inquiries, process returns, answer FAQs
- **Research Assistants** - Gather information, summarize documents, analyze data
- **Workflow Automation** - Multi-step business processes with AI decision-making
- **Code Assistants** - Help with code review, documentation, debugging
- **Data Processing Pipelines** - Extract, transform, analyze data at scale

### Which AI models are supported?

| Provider | Models |
|----------|--------|
| Anthropic | Claude 3 Opus, Sonnet, Haiku |
| OpenAI | GPT-4, GPT-4 Turbo, GPT-3.5 |
| Google | Gemini Pro, Gemini Ultra |
| Local | Ollama, LMStudio, vLLM |

### Is my data secure?

Yes. We implement:
- End-to-end encryption (TLS 1.3)
- Encryption at rest (AES-256)
- SOC 2 Type II compliance
- GDPR compliance
- Optional HIPAA compliance (Enterprise)

See our [Security Guide](security.md) for details.

---

## Getting Started

### How do I get started?

1. Sign up at [gagiteck.com](https://www.gagiteck.com)
2. Create your first agent in the dashboard
3. Or follow our [Quick Start Guide](quickstart.md)

### What are the system requirements?

For self-hosted deployment:
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 20+ GB SSD
- **OS**: Linux, macOS, or Windows with WSL2

### How do I get my API key?

1. Log into the Gagiteck dashboard
2. Go to Settings > API Keys
3. Click "Create New Key"
4. Copy and securely store the key (it's only shown once)

---

## Agents

### What's the difference between an agent and a chatbot?

| Feature | Chatbot | Gagiteck Agent |
|---------|---------|----------------|
| Conversation | Yes | Yes |
| Tool Usage | Limited | Full |
| Autonomous Actions | No | Yes |
| Multi-step Reasoning | Limited | Yes |
| Memory | Session only | Persistent |
| Workflow Integration | No | Yes |

### How many agents can I create?

| Plan | Agents |
|------|--------|
| Free | 3 |
| Pro | 25 |
| Enterprise | Unlimited |

### Can agents call external APIs?

Yes! Agents can use tools to:
- Make HTTP requests
- Query databases
- Send emails/messages
- Interact with any API

See [Integrations Guide](integrations.md).

### How do I give an agent memory?

```python
agent = client.agents.create(
    name="Personal Assistant",
    memory_enabled=True,
    memory_type="long_term",  # Persists across conversations
    memory_window=50          # Messages to retain
)
```

---

## Workflows

### What's a workflow?

A workflow is a sequence of steps that orchestrate multiple agents to complete complex tasks. Think of it as a pipeline where each step can:
- Run an agent
- Make decisions based on conditions
- Execute in parallel
- Handle errors gracefully

### Can workflows run on a schedule?

Yes! Use cron expressions:

```yaml
trigger:
  type: schedule
  cron: "0 9 * * 1-5"  # 9 AM, Monday-Friday
  timezone: America/New_York
```

### How do I pass data between workflow steps?

Use template variables:

```yaml
steps:
  - id: step1
    agent: researcher
    input: "Research {{inputs.topic}}"

  - id: step2
    agent: writer
    input: "Write about: {{steps.step1.output}}"
    depends_on: [step1]
```

---

## Pricing & Billing

### What's included in the free plan?

- 3 agents
- 1 workflow
- 1,000 API calls/month
- 1 GB storage
- Community support

### How is usage calculated?

Usage is based on:
1. **API Calls** - Each agent execution or API request
2. **Tokens** - LLM tokens consumed (input + output)
3. **Storage** - Files and data stored

### Do unused credits roll over?

Monthly API calls reset each billing cycle. Token credits on annual plans roll over for up to 3 months.

### Can I upgrade or downgrade anytime?

Yes. Upgrades take effect immediately. Downgrades apply at the next billing cycle.

---

## Technical

### What programming languages are supported?

Official SDKs:
- Python 3.8+
- Node.js 18+
- Go 1.20+

Any language can use the REST API.

### Is there a rate limit?

| Plan | Requests/minute |
|------|-----------------|
| Free | 60 |
| Pro | 600 |
| Enterprise | 6,000+ |

### How do I handle errors?

```python
from gagiteck import Client, GagiteckError

client = Client(api_key="YOUR_KEY")

try:
    response = client.agents.run(agent_id="agent_123", message="Hello")
except GagiteckError as e:
    print(f"Error: {e.code} - {e.message}")
```

### Can I run Gagiteck on-premise?

Yes, Enterprise plans include on-premise deployment options. Contact sales@gagiteck.com.

---

## Integrations

### Which services can I integrate?

50+ integrations including:
- **Communication**: Slack, Discord, Email, Teams
- **Development**: GitHub, GitLab, Jira, Linear
- **CRM**: Salesforce, HubSpot, Pipedrive
- **Data**: PostgreSQL, MongoDB, BigQuery

See [Integrations Guide](integrations.md).

### Can I build custom integrations?

Yes! Create custom tools using:
- HTTP/REST APIs
- GraphQL
- Webhooks
- Database connections

```python
@tool
def my_custom_integration(param: str) -> dict:
    """My custom tool."""
    return requests.get(f"https://api.example.com/{param}").json()
```

---

## Troubleshooting

### My agent isn't responding

1. Check API key validity
2. Verify agent status is "active"
3. Check rate limits
4. Review error logs in dashboard

### Agent responses are slow

1. Try a faster model (Haiku vs Opus)
2. Reduce max_tokens
3. Simplify system prompt
4. Check network latency

### Tool calls are failing

1. Verify tool permissions
2. Check external API status
3. Review tool input/output logs
4. Test tool in isolation

### How do I debug an agent?

```python
response = client.agents.run(
    agent_id="agent_123",
    message="Debug this",
    debug=True
)

print(response.debug.reasoning_trace)
print(response.debug.tool_calls)
```

---

## Support

### How do I get help?

- **Documentation**: [docs/](.)
- **Community**: [GitHub Discussions](https://github.com/gagiteck/gagiteck-assets/discussions)
- **Email**: support@gagiteck.com
- **Enterprise**: Dedicated Slack channel

### How do I report a bug?

1. Check existing [GitHub Issues](https://github.com/gagiteck/gagiteck-assets/issues)
2. Create a new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Error messages/logs

### Is there a status page?

Yes: [status.gagiteck.com](https://status.gagiteck.com)

Subscribe for incident notifications.
