# Workflows Guide

Workflows enable you to orchestrate multiple AI agents and automate complex multi-step processes.

## Overview

A **Workflow** is a directed acyclic graph (DAG) of steps that:
- Execute agents in sequence or parallel
- Pass data between steps
- Handle errors and retries
- Trigger on events or schedules

---

## Creating Workflows

### Using YAML

```yaml
# workflows/customer-onboarding.yaml
name: Customer Onboarding
description: Automated onboarding for new customers
version: 1.0.0

# Trigger configuration
trigger:
  type: event
  event: customer.created

# Input schema
inputs:
  customer:
    type: object
    properties:
      id: { type: string }
      name: { type: string }
      email: { type: string }
      company: { type: string }

# Workflow steps
steps:
  - id: verify_email
    name: Verify Email Address
    agent: verification-agent
    input: |
      Verify the email address: {{inputs.customer.email}}
      Send a verification code.

  - id: create_workspace
    name: Create Customer Workspace
    agent: provisioning-agent
    input: |
      Create a new workspace for customer: {{inputs.customer.name}}
      Company: {{inputs.customer.company}}
    depends_on: [verify_email]

  - id: send_welcome
    name: Send Welcome Email
    agent: communication-agent
    input: |
      Send a personalized welcome email to {{inputs.customer.name}}
      at {{inputs.customer.email}}.
      Include getting started guide and support contacts.
    depends_on: [create_workspace]

  - id: schedule_onboarding
    name: Schedule Onboarding Call
    agent: scheduling-agent
    input: |
      Schedule an onboarding call with {{inputs.customer.name}}.
      Customer email: {{inputs.customer.email}}
    depends_on: [create_workspace]

# Output configuration
output:
  workspace_id: "{{steps.create_workspace.output.workspace_id}}"
  welcome_sent: "{{steps.send_welcome.status == 'completed'}}"
  onboarding_scheduled: "{{steps.schedule_onboarding.output.meeting_link}}"
```

### Using the API

```python
from gagiteck import Client

client = Client(api_key="YOUR_API_KEY")

workflow = client.workflows.create(
    name="Customer Onboarding",
    trigger={"type": "event", "event": "customer.created"},
    steps=[
        {
            "id": "verify_email",
            "agent_id": "agent_verification",
            "input": "Verify email: {{inputs.customer.email}}"
        },
        {
            "id": "create_workspace",
            "agent_id": "agent_provisioning",
            "input": "Create workspace for {{inputs.customer.name}}",
            "depends_on": ["verify_email"]
        }
    ]
)
```

---

## Step Configuration

### Basic Step

```yaml
steps:
  - id: unique_step_id
    name: Human-readable name
    agent: agent-name-or-id
    input: "Prompt template with {{variables}}"
```

### Step with All Options

```yaml
steps:
  - id: process_order
    name: Process Customer Order
    agent: order-processing-agent

    # Input prompt (supports templating)
    input: |
      Process the following order:
      Order ID: {{inputs.order_id}}
      Customer: {{inputs.customer_name}}
      Items: {{inputs.items | json}}

    # Dependencies
    depends_on: [validate_order, check_inventory]

    # Execution settings
    timeout_ms: 60000
    retry:
      max_attempts: 3
      delay_ms: 5000
      backoff: exponential

    # Conditional execution
    condition: "{{inputs.order_total > 0}}"

    # Error handling
    on_error: continue  # or: fail, retry, skip

    # Output transformation
    output_transform:
      order_confirmed: "{{output.status == 'confirmed'}}"
      tracking_number: "{{output.tracking}}"
```

---

## Control Flow

### Sequential Execution

```yaml
steps:
  - id: step1
    agent: agent-a
    input: "First step"

  - id: step2
    agent: agent-b
    input: "Second step"
    depends_on: [step1]

  - id: step3
    agent: agent-c
    input: "Third step"
    depends_on: [step2]
```

### Parallel Execution

```yaml
steps:
  - id: start
    agent: agent-init
    input: "Initialize"

  # These run in parallel
  - id: task_a
    agent: agent-a
    input: "Task A"
    depends_on: [start]

  - id: task_b
    agent: agent-b
    input: "Task B"
    depends_on: [start]

  - id: task_c
    agent: agent-c
    input: "Task C"
    depends_on: [start]

  # Wait for all parallel tasks
  - id: finish
    agent: agent-final
    input: "Combine results from A, B, C"
    depends_on: [task_a, task_b, task_c]
```

### Conditional Branching

```yaml
steps:
  - id: classify
    agent: classifier-agent
    input: "Classify this request: {{inputs.request}}"

  - id: handle_billing
    agent: billing-agent
    input: "Handle billing request"
    depends_on: [classify]
    condition: "{{steps.classify.output.category == 'billing'}}"

  - id: handle_support
    agent: support-agent
    input: "Handle support request"
    depends_on: [classify]
    condition: "{{steps.classify.output.category == 'support'}}"

  - id: handle_sales
    agent: sales-agent
    input: "Handle sales request"
    depends_on: [classify]
    condition: "{{steps.classify.output.category == 'sales'}}"
```

---

## Triggers

### Event Trigger

```yaml
trigger:
  type: event
  event: customer.created
  filters:
    - field: customer.plan
      operator: equals
      value: enterprise
```

### Schedule Trigger

```yaml
trigger:
  type: schedule
  cron: "0 9 * * 1"  # Every Monday at 9 AM
  timezone: America/New_York
```

### Webhook Trigger

```yaml
trigger:
  type: webhook
  path: /webhooks/process-order
  method: POST
  authentication:
    type: api_key
    header: X-Webhook-Secret
```

### Manual Trigger

```yaml
trigger:
  type: manual
```

---

## Data & Variables

### Input Variables

```yaml
inputs:
  customer_id:
    type: string
    required: true

  amount:
    type: number
    default: 0

  options:
    type: object
    properties:
      priority:
        type: string
        enum: [low, medium, high]
```

### Accessing Data

```yaml
# Access input data
input: "Process customer {{inputs.customer_id}}"

# Access previous step output
input: "Continue with {{steps.previous_step.output}}"

# Access nested data
input: "Email: {{steps.get_customer.output.customer.email}}"

# Use filters
input: "Items: {{inputs.items | json}}"
input: "Total: {{inputs.amount | currency}}"
input: "Date: {{inputs.timestamp | date:'YYYY-MM-DD'}}"
```

### Environment Variables

```yaml
steps:
  - id: api_call
    agent: api-agent
    input: "Call API at {{env.API_ENDPOINT}}"
    environment:
      API_KEY: "{{secrets.EXTERNAL_API_KEY}}"
```

---

## Error Handling

### Retry Configuration

```yaml
steps:
  - id: flaky_api
    agent: api-agent
    input: "Call external API"
    retry:
      max_attempts: 5
      delay_ms: 1000
      backoff: exponential  # 1s, 2s, 4s, 8s, 16s
      retry_on:
        - timeout
        - rate_limit
        - server_error
```

### Error Strategies

```yaml
steps:
  - id: critical_step
    on_error: fail  # Stop entire workflow

  - id: optional_step
    on_error: skip  # Continue to next step

  - id: recoverable_step
    on_error: retry  # Retry with backoff

  - id: fallback_step
    on_error: fallback
    fallback:
      agent: fallback-agent
      input: "Handle error: {{error.message}}"
```

### Global Error Handler

```yaml
on_error:
  notify:
    - type: slack
      channel: "#alerts"
      message: "Workflow failed: {{workflow.name}}"
    - type: email
      to: "ops@gagiteck.com"
```

---

## Monitoring & Debugging

### View Workflow Runs

```python
# List recent runs
runs = client.workflows.list_runs(
    workflow_id="wf_123",
    status="failed",
    limit=10
)

for run in runs:
    print(f"Run {run.id}: {run.status}")
    for step in run.steps:
        print(f"  {step.id}: {step.status} ({step.duration_ms}ms)")
```

### Get Run Details

```python
run = client.workflows.get_run(run_id="run_abc123")

print(f"Status: {run.status}")
print(f"Duration: {run.duration_ms}ms")

for step in run.steps:
    print(f"\nStep: {step.name}")
    print(f"  Status: {step.status}")
    print(f"  Input: {step.input}")
    print(f"  Output: {step.output}")
    if step.error:
        print(f"  Error: {step.error}")
```

### Workflow Logs

```python
logs = client.workflows.get_logs(run_id="run_abc123")

for log in logs:
    print(f"[{log.timestamp}] {log.level}: {log.message}")
```

---

## Examples

### Data Pipeline

```yaml
name: Daily Data Pipeline
trigger:
  type: schedule
  cron: "0 2 * * *"  # 2 AM daily

steps:
  - id: extract
    name: Extract Data
    agent: etl-agent
    input: "Extract data from {{env.SOURCE_DB}} for yesterday"

  - id: transform
    name: Transform Data
    agent: etl-agent
    input: |
      Transform the extracted data:
      {{steps.extract.output | json}}
      Apply business rules and clean data.
    depends_on: [extract]

  - id: validate
    name: Validate Data
    agent: validation-agent
    input: "Validate transformed data quality"
    depends_on: [transform]

  - id: load
    name: Load to Warehouse
    agent: etl-agent
    input: "Load validated data to {{env.WAREHOUSE_DB}}"
    depends_on: [validate]

  - id: notify
    name: Send Report
    agent: notification-agent
    input: "Send daily ETL report to data team"
    depends_on: [load]
```

### Content Generation Pipeline

```yaml
name: Blog Post Generator
trigger:
  type: manual

inputs:
  topic:
    type: string
    required: true

steps:
  - id: research
    agent: research-agent
    input: "Research the topic: {{inputs.topic}}"

  - id: outline
    agent: writer-agent
    input: |
      Create a blog post outline based on research:
      {{steps.research.output}}
    depends_on: [research]

  - id: write
    agent: writer-agent
    input: |
      Write a full blog post from this outline:
      {{steps.outline.output}}
    depends_on: [outline]

  - id: edit
    agent: editor-agent
    input: "Edit and improve: {{steps.write.output}}"
    depends_on: [write]

  - id: seo_optimize
    agent: seo-agent
    input: "Optimize for SEO: {{steps.edit.output}}"
    depends_on: [edit]

output:
  blog_post: "{{steps.seo_optimize.output}}"
```

---

## Related Documentation

- [Agents Guide](agents.md)
- [API Reference](api-reference.md)
- [Integrations](integrations.md)
