# Security Guide

Comprehensive security documentation for the Gagiteck AI SaaS Platform.

## Security Overview

Gagiteck implements security at multiple layers:
- **Infrastructure** - Network isolation, encryption at rest
- **Application** - Authentication, authorization, input validation
- **Data** - Encryption, access controls, audit logging
- **AI Safety** - Content filtering, output validation

---

## Authentication

### API Key Authentication

```bash
# API key in header (recommended)
curl -H "Authorization: Bearer ggt_your_api_key" \
  https://api.gagiteck.com/v1/agents

# API key in query parameter
curl "https://api.gagiteck.com/v1/agents?api_key=ggt_your_api_key"
```

### API Key Management

```python
from gagiteck import Client

client = Client(api_key="ggt_admin_key")

# Create new API key
key = client.api_keys.create(
    name="Production API",
    scopes=["agents:read", "agents:run"],
    expires_at="2025-12-31T23:59:59Z"
)

print(f"Key: {key.key}")  # Only shown once!
print(f"ID: {key.id}")

# List keys
keys = client.api_keys.list()

# Revoke key
client.api_keys.revoke(key_id="key_123")
```

### JWT Authentication

```python
# Exchange credentials for JWT
response = client.auth.login(
    email="user@example.com",
    password="secure_password"
)

access_token = response.access_token
refresh_token = response.refresh_token

# Use JWT for API calls
client = Client(token=access_token)

# Refresh token when expired
new_tokens = client.auth.refresh(refresh_token)
```

### OAuth 2.0 / OIDC

```python
# Initiate OAuth flow
auth_url = client.auth.get_oauth_url(
    provider="google",
    redirect_uri="https://yourapp.com/callback",
    state="random_state_token"
)

# After user authorizes, exchange code
tokens = client.auth.exchange_oauth_code(
    provider="google",
    code="authorization_code",
    redirect_uri="https://yourapp.com/callback"
)
```

### Enterprise SSO (SAML)

```yaml
# SAML configuration
auth:
  saml:
    enabled: true
    entity_id: "https://api.gagiteck.com/saml"
    acs_url: "https://api.gagiteck.com/saml/acs"
    slo_url: "https://api.gagiteck.com/saml/slo"

    idp:
      metadata_url: "https://idp.company.com/metadata.xml"
      # Or inline configuration:
      # sso_url: "https://idp.company.com/sso"
      # certificate: "-----BEGIN CERTIFICATE-----..."

    attribute_mapping:
      email: "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
      name: "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
      groups: "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups"
```

---

## Authorization

### Role-Based Access Control (RBAC)

| Role | Description | Permissions |
|------|-------------|-------------|
| **Owner** | Organization owner | Full access |
| **Admin** | Administrator | Manage users, agents, settings |
| **Developer** | Create and manage | Create/edit agents and workflows |
| **Operator** | Run and monitor | Execute agents, view logs |
| **Viewer** | Read-only | View agents and executions |

### Permission Matrix

| Resource | Owner | Admin | Developer | Operator | Viewer |
|----------|-------|-------|-----------|----------|--------|
| Agents - Create | ✓ | ✓ | ✓ | - | - |
| Agents - Run | ✓ | ✓ | ✓ | ✓ | - |
| Agents - Delete | ✓ | ✓ | - | - | - |
| Workflows - Create | ✓ | ✓ | ✓ | - | - |
| Workflows - Trigger | ✓ | ✓ | ✓ | ✓ | - |
| Settings - Modify | ✓ | ✓ | - | - | - |
| Billing - View | ✓ | ✓ | - | - | - |
| Users - Manage | ✓ | ✓ | - | - | - |

### API Key Scopes

```python
# Create key with limited scopes
key = client.api_keys.create(
    name="Read-only Key",
    scopes=[
        "agents:read",
        "workflows:read",
        "executions:read"
    ]
)

# Available scopes
scopes = [
    "agents:read",
    "agents:write",
    "agents:run",
    "agents:delete",
    "workflows:read",
    "workflows:write",
    "workflows:trigger",
    "executions:read",
    "integrations:read",
    "integrations:write",
    "settings:read",
    "settings:write",
    "users:read",
    "users:write",
    "billing:read"
]
```

---

## Data Security

### Encryption at Rest

All data is encrypted using AES-256-GCM:

```yaml
security:
  encryption:
    algorithm: aes-256-gcm
    key_management: aws-kms  # or vault, local

    # AWS KMS configuration
    kms:
      key_id: "arn:aws:kms:us-east-1:123456789:key/abc-123"
      region: us-east-1
```

### Encryption in Transit

- All API traffic uses TLS 1.3
- Certificate pinning available for SDKs
- mTLS supported for enterprise

```yaml
security:
  tls:
    min_version: "1.3"
    cipher_suites:
      - TLS_AES_256_GCM_SHA384
      - TLS_CHACHA20_POLY1305_SHA256
```

### Secrets Management

```python
# Store secrets securely
client.secrets.create(
    name="OPENAI_API_KEY",
    value="sk-...",
    scope="organization"  # or "agent", "workflow"
)

# Use in agents (value never exposed)
agent = client.agents.create(
    name="AI Assistant",
    environment={
        "API_KEY": "{{secrets.OPENAI_API_KEY}}"
    }
)
```

---

## Audit Logging

### Log Types

| Event | Description |
|-------|-------------|
| `auth.login` | User login attempt |
| `auth.logout` | User logout |
| `agent.created` | Agent created |
| `agent.run` | Agent executed |
| `workflow.triggered` | Workflow started |
| `api_key.created` | New API key |
| `settings.changed` | Configuration modified |

### Accessing Audit Logs

```python
# Query audit logs
logs = client.audit.list(
    start_date="2025-01-01",
    end_date="2025-01-31",
    event_types=["agent.run", "workflow.triggered"],
    actor_id="user_123"
)

for log in logs:
    print(f"{log.timestamp} - {log.event_type}")
    print(f"  Actor: {log.actor.email}")
    print(f"  Resource: {log.resource_type}/{log.resource_id}")
    print(f"  IP: {log.ip_address}")
```

### Log Retention

```yaml
audit:
  retention:
    default: 90d
    auth_events: 365d
    compliance: 7y
  export:
    enabled: true
    destination: s3://audit-logs-bucket
    format: json
```

---

## AI Safety

### Content Filtering

```python
# Enable content filtering on agent
agent = client.agents.create(
    name: "Customer Support",
    content_filter={
        "enabled": True,
        "block_categories": [
            "violence",
            "hate_speech",
            "adult_content",
            "personally_identifiable_information"
        ],
        "custom_filters": [
            {"pattern": r"\b\d{3}-\d{2}-\d{4}\b", "action": "redact"},  # SSN
            {"pattern": r"\b\d{16}\b", "action": "block"}  # Credit card
        ]
    }
)
```

### Output Validation

```python
# Validate agent outputs
agent = client.agents.create(
    name="Data Agent",
    output_validation={
        "schema": {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["result"]
        },
        "on_invalid": "retry"  # or "fail", "sanitize"
    }
)
```

### Tool Permissions

```python
# Restrict tool capabilities
agent = client.agents.create(
    name="Restricted Agent",
    tool_permissions={
        "http_request": {
            "allowed_domains": ["api.example.com", "api.trusted.com"],
            "blocked_methods": ["DELETE", "PUT"]
        },
        "file_read": {
            "allowed_paths": ["/data/public/*"],
            "max_file_size_mb": 10
        },
        "sql_query": {
            "read_only": True,
            "allowed_tables": ["products", "categories"]
        }
    }
)
```

---

## Network Security

### IP Allowlisting

```yaml
security:
  network:
    ip_allowlist:
      enabled: true
      addresses:
        - 192.168.1.0/24
        - 10.0.0.0/8
      apply_to:
        - api
        - dashboard
```

### Rate Limiting

```yaml
security:
  rate_limit:
    global:
      requests: 10000
      window: 60s

    per_user:
      requests: 1000
      window: 60s

    per_endpoint:
      "/v1/agents/*/run":
        requests: 100
        window: 60s
```

### WAF Rules

```yaml
security:
  waf:
    enabled: true
    rules:
      - sql_injection: block
      - xss: block
      - path_traversal: block
      - request_size: 10mb
```

---

## Compliance

### SOC 2 Type II

Gagiteck maintains SOC 2 Type II compliance:
- Security controls
- Availability monitoring
- Processing integrity
- Confidentiality measures
- Privacy controls

### GDPR

```python
# Data subject access request
data = client.compliance.export_user_data(user_id="user_123")

# Right to be forgotten
client.compliance.delete_user_data(
    user_id="user_123",
    confirmation_token="token_from_email"
)
```

### HIPAA

Enterprise customers can enable HIPAA-compliant mode:

```yaml
compliance:
  hipaa:
    enabled: true
    phi_detection: true
    audit_all_access: true
    encryption_required: true
```

---

## Incident Response

### Security Contacts

Report security issues to: security@gagiteck.com

### Bug Bounty

We maintain a bug bounty program for responsible disclosure.

### Incident Notification

Enterprise customers receive:
- Real-time security alerts
- 24-hour breach notification
- Post-incident reports

---

## Best Practices

### API Key Security

1. Never commit API keys to source control
2. Use environment variables or secrets managers
3. Rotate keys regularly
4. Use scoped keys with minimum permissions
5. Set expiration dates on keys

### Agent Security

1. Validate all user inputs
2. Use content filtering
3. Restrict tool permissions
4. Monitor agent behavior
5. Review outputs before external actions

### Network Security

1. Use IP allowlisting in production
2. Enable rate limiting
3. Use TLS for all connections
4. Implement WAF rules
5. Monitor for anomalies

---

## Related Documentation

- [Authentication Guide](authentication.md)
- [Configuration Guide](configuration.md)
- [API Reference](api-reference.md)
