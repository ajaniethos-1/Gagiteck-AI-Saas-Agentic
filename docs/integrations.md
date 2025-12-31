# Integrations Guide

Connect your Gagiteck agents and workflows to external services and APIs.

## Overview

Gagiteck integrates with:
- **SaaS Applications** - Slack, GitHub, Salesforce, etc.
- **Databases** - PostgreSQL, MongoDB, Redis
- **APIs** - REST, GraphQL, webhooks
- **Cloud Services** - AWS, GCP, Azure

---

## Built-in Connectors

### Communication

| Connector | Features |
|-----------|----------|
| **Slack** | Send messages, create channels, manage users |
| **Discord** | Bot integration, message handling |
| **Email (SMTP)** | Send/receive emails |
| **Twilio** | SMS, voice calls |
| **Microsoft Teams** | Messages, meetings |

### Development

| Connector | Features |
|-----------|----------|
| **GitHub** | Issues, PRs, repositories, actions |
| **GitLab** | Projects, merge requests, CI/CD |
| **Jira** | Issues, sprints, projects |
| **Linear** | Issues, projects, cycles |
| **Notion** | Pages, databases, blocks |

### CRM & Sales

| Connector | Features |
|-----------|----------|
| **Salesforce** | Leads, opportunities, contacts |
| **HubSpot** | CRM, marketing, sales |
| **Pipedrive** | Deals, contacts, activities |

### Data & Analytics

| Connector | Features |
|-----------|----------|
| **PostgreSQL** | Full SQL access |
| **MongoDB** | Document operations |
| **BigQuery** | Analytics queries |
| **Snowflake** | Data warehouse |

---

## Setting Up Integrations

### OAuth Connections

```python
from gagiteck import Client

client = Client(api_key="YOUR_API_KEY")

# Initiate OAuth flow
auth_url = client.integrations.connect(
    provider="slack",
    redirect_uri="https://yourapp.com/oauth/callback",
    scopes=["chat:write", "channels:read"]
)

# User visits auth_url and authorizes
# After callback:
connection = client.integrations.complete_oauth(
    provider="slack",
    code="oauth_code_from_callback"
)

print(f"Connected: {connection.id}")
```

### API Key Connections

```python
connection = client.integrations.create(
    provider="openai",
    credentials={
        "api_key": "sk-..."
    }
)
```

### Webhook Configuration

```python
webhook = client.integrations.create_webhook(
    name="GitHub Events",
    url="https://api.gagiteck.com/webhooks/github",
    events=["push", "pull_request", "issues"],
    secret="webhook_secret_123"
)

print(f"Webhook URL: {webhook.url}")
```

---

## Using Integrations in Agents

### Slack Integration

```python
from gagiteck import Client, tool
from gagiteck.integrations import slack

@tool
def send_slack_message(channel: str, message: str) -> dict:
    """Send a message to a Slack channel."""
    return slack.post_message(
        channel=channel,
        text=message
    )

@tool
def create_slack_channel(name: str, is_private: bool = False) -> dict:
    """Create a new Slack channel."""
    return slack.create_channel(
        name=name,
        is_private=is_private
    )

agent = client.agents.create(
    name="Slack Bot",
    tools=[send_slack_message, create_slack_channel],
    system_prompt="You help manage Slack communications."
)
```

### GitHub Integration

```python
from gagiteck.integrations import github

@tool
def create_github_issue(
    repo: str,
    title: str,
    body: str,
    labels: list = None
) -> dict:
    """Create a GitHub issue."""
    return github.create_issue(
        repo=repo,
        title=title,
        body=body,
        labels=labels or []
    )

@tool
def get_pull_requests(repo: str, state: str = "open") -> list:
    """Get pull requests from a repository."""
    return github.list_pull_requests(
        repo=repo,
        state=state
    )

agent = client.agents.create(
    name="GitHub Assistant",
    tools=[create_github_issue, get_pull_requests],
    system_prompt="You help manage GitHub repositories."
)
```

### Database Integration

```python
from gagiteck.integrations import database

# Configure database connection
db = database.connect(
    type="postgresql",
    connection_string="postgresql://user:pass@host:5432/db"
)

@tool
def query_database(sql: str) -> list:
    """Execute a read-only SQL query."""
    return db.query(sql, read_only=True)

@tool
def get_customer(customer_id: str) -> dict:
    """Get customer by ID."""
    result = db.query(
        "SELECT * FROM customers WHERE id = %s",
        params=[customer_id]
    )
    return result[0] if result else None
```

---

## Webhooks

### Receiving Webhooks

Configure webhooks to trigger workflows:

```yaml
# workflow.yaml
name: GitHub PR Review
trigger:
  type: webhook
  path: /webhooks/github
  events:
    - pull_request.opened
    - pull_request.synchronize

steps:
  - id: review_code
    agent: code-reviewer
    input: |
      Review this pull request:
      Title: {{webhook.pull_request.title}}
      URL: {{webhook.pull_request.html_url}}
      Changes: {{webhook.pull_request.diff_url}}
```

### Sending Webhooks

```python
@tool
def notify_external_system(event: str, data: dict) -> dict:
    """Send webhook to external system."""
    import requests

    response = requests.post(
        "https://external-system.com/webhook",
        json={
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Authorization": f"Bearer {secrets.WEBHOOK_TOKEN}"
        }
    )
    return response.json()
```

---

## Custom Integrations

### HTTP Tool

For any REST API:

```python
from gagiteck.integrations import http

@tool
def call_custom_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Call a custom REST API."""
    return http.request(
        url=f"https://api.example.com{endpoint}",
        method=method,
        json=data,
        headers={
            "Authorization": f"Bearer {secrets.API_TOKEN}"
        }
    )
```

### GraphQL Tool

```python
from gagiteck.integrations import graphql

client = graphql.Client(
    endpoint="https://api.example.com/graphql",
    headers={"Authorization": f"Bearer {secrets.TOKEN}"}
)

@tool
def graphql_query(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query."""
    return client.execute(query, variables)
```

---

## Authentication Methods

### OAuth 2.0

```python
# Supported OAuth providers
oauth_providers = [
    "google",
    "github",
    "slack",
    "salesforce",
    "microsoft",
    "hubspot"
]

# Initialize OAuth flow
auth_url = client.integrations.get_oauth_url(
    provider="salesforce",
    scopes=["api", "refresh_token"],
    state="unique_state_token"
)
```

### API Keys

```python
connection = client.integrations.create(
    provider="custom",
    name="External API",
    auth_type="api_key",
    credentials={
        "api_key": "your-api-key",
        "header_name": "X-API-Key"
    }
)
```

### Basic Auth

```python
connection = client.integrations.create(
    provider="custom",
    name="Legacy System",
    auth_type="basic",
    credentials={
        "username": "user",
        "password": "pass"
    }
)
```

---

## Security Best Practices

### Credential Storage

```python
# Store credentials as secrets
client.secrets.create(
    name="SALESFORCE_TOKEN",
    value="encrypted_token_value"
)

# Reference in integrations
@tool
def salesforce_query(query: str) -> list:
    return salesforce.query(
        query,
        token=secrets.SALESFORCE_TOKEN
    )
```

### Scope Limitation

```python
# Request minimum required scopes
connection = client.integrations.connect(
    provider="github",
    scopes=[
        "repo:read",      # Read-only repo access
        "issues:write"    # Write issues only
    ]
)
```

### IP Allowlisting

```yaml
# config.yaml
integrations:
  security:
    allowed_ips:
      - 192.168.1.0/24
      - 10.0.0.0/8
    blocked_domains:
      - example.com
```

---

## Troubleshooting

### Connection Issues

```python
# Test connection
status = client.integrations.test(connection_id="conn_123")

if not status.connected:
    print(f"Error: {status.error}")
    print(f"Last successful: {status.last_success}")
```

### Rate Limiting

```python
# Check rate limit status
limits = client.integrations.get_rate_limits(provider="github")

print(f"Remaining: {limits.remaining}/{limits.limit}")
print(f"Resets at: {limits.reset_at}")
```

---

## Related Documentation

- [Agents Guide](agents.md)
- [Workflows Guide](workflows.md)
- [API Reference](api-reference.md)
