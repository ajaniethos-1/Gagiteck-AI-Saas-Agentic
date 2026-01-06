# Gagiteck User Guide

Welcome to Gagiteck! This guide will help you get started with building and deploying AI agents.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Creating Agents](#creating-agents)
4. [Building Workflows](#building-workflows)
5. [Monitoring Executions](#monitoring-executions)
6. [Managing Settings](#managing-settings)
7. [Team Collaboration](#team-collaboration)
8. [Best Practices](#best-practices)

---

## Getting Started

### 1. Sign Up

1. Visit [app.mimoai.co](https://app.mimoai.co)
2. Click "Sign Up" and enter your details
3. Verify your email address
4. Complete the onboarding wizard

### 2. First Steps

When you first log in, you'll see the onboarding checklist:

- [ ] Create your first agent
- [ ] Build a workflow
- [ ] Run an execution

Complete these steps to familiarize yourself with the platform.

---

## Dashboard Overview

The dashboard is your command center for all AI operations.

### Navigation

| Menu Item | Description |
|-----------|-------------|
| **Dashboard** | Overview stats and recent activity |
| **Agents** | Create and manage AI agents |
| **Workflows** | Build multi-step automations |
| **Executions** | Monitor running and past executions |
| **Settings** | Account, API keys, team settings |

### Quick Actions

From the dashboard, you can quickly:
- Create a new agent
- Start a new workflow
- View recent executions

### Stats Overview

- **Total Agents**: Number of agents you've created
- **Active Workflows**: Workflows currently enabled
- **Executions**: Total runs across all agents/workflows
- **Success Rate**: Percentage of successful executions

---

## Creating Agents

Agents are autonomous AI assistants that can perform tasks using tools and instructions you define.

### Step 1: Basic Information

1. Go to **Agents** > **Create Agent**
2. Enter a descriptive name (e.g., "Customer Support Bot")
3. Write a system prompt that defines the agent's personality and capabilities

**Example System Prompt:**
```
You are a helpful customer support agent for TechCorp.

Your responsibilities:
- Answer product questions
- Help troubleshoot issues
- Escalate complex problems to human agents

Always be polite, professional, and concise.
```

### Step 2: Configuration

| Setting | Description | Recommended |
|---------|-------------|-------------|
| **Model** | AI model to use | Claude 3 Sonnet |
| **Max Tokens** | Maximum response length | 4096 |
| **Temperature** | Creativity (0=focused, 2=creative) | 0.7 |
| **Max Iterations** | Tool use cycles | 25 |
| **Timeout** | Max execution time | 120s |

### Step 3: Add Tools

Tools extend your agent's capabilities:

- **web_search**: Search the internet
- **calculator**: Perform calculations
- **code_interpreter**: Execute Python code
- **knowledge_base**: Query your documents
- **api_call**: Make HTTP requests

### Step 4: Test Your Agent

1. Click **Run** on the agent card
2. Enter a test message
3. Review the response
4. Adjust settings as needed

---

## Building Workflows

Workflows chain multiple agents and actions together for complex automations.

### Creating a Workflow

1. Go to **Workflows** > **Create Workflow**
2. Name your workflow
3. Add a description

### Adding Steps

Click **Add Step** and choose from:

| Step Type | Description |
|-----------|-------------|
| **Agent** | Run an AI agent |
| **Condition** | Branch based on logic |
| **Delay** | Wait before next step |
| **Webhook** | Call external API |

### Step Configuration

#### Agent Step
```
Agent: Research Assistant
Message: Research the topic: {{input.topic}}
```

#### Condition Step
```
If: {{previous.sentiment}} == "negative"
Then: Go to step "Escalate"
Else: Go to step "Respond"
```

#### Webhook Step
```
URL: https://api.slack.com/webhook
Method: POST
Body: {"text": "{{previous.summary}}"}
```

### Variables

Use variables to pass data between steps:

- `{{input.variable}}` - Workflow input
- `{{step_name.output}}` - Previous step output
- `{{env.VARIABLE}}` - Environment variable

### Testing Workflows

1. Click **Trigger** on the workflow
2. Enter test input values
3. Monitor execution progress
4. Review each step's output

---

## Monitoring Executions

### Execution List

The Executions page shows all running and completed executions:

| Column | Description |
|--------|-------------|
| **ID** | Unique execution identifier |
| **Type** | Agent or Workflow |
| **Status** | Running, Completed, Failed, Cancelled |
| **Started** | When execution began |
| **Duration** | How long it took |

### Status Indicators

- 🟢 **Completed**: Successfully finished
- 🔵 **Running**: Currently executing
- 🔴 **Failed**: Error occurred
- ⚪ **Cancelled**: Manually stopped

### Execution Details

Click any execution to view:
- Input parameters
- Output results
- Error messages (if failed)
- Step-by-step breakdown (for workflows)
- Token usage

### Cancelling Executions

For running executions, click the **Stop** button to cancel.

---

## Managing Settings

### Profile

Update your personal information:
- Display name
- Email (contact support to change)
- Password

### API Keys

Create API keys for programmatic access:

1. Go to **Settings** > **API Keys**
2. Click **Create Key**
3. Name your key (e.g., "Production Server")
4. Copy and securely store the key

**Important:** Keys are only shown once. Store them securely!

### Notifications

Configure how you receive alerts:

| Setting | Description |
|---------|-------------|
| **Email Alerts** | Important notifications |
| **Execution Failures** | When runs fail |
| **Weekly Digest** | Summary of activity |

### Security

- **Change Password**: Update your password
- **Two-Factor Auth**: Add extra security (coming soon)

---

## Team Collaboration

### Inviting Members

1. Go to **Settings** > **Team**
2. Click **Invite Member**
3. Enter their email
4. Select a role

### Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, manage team |
| **Developer** | Create/edit agents and workflows |
| **Operator** | Run agents, view executions |
| **Viewer** | Read-only access |

### Managing Members

- Change member roles
- Remove members
- View activity history

---

## Best Practices

### Agent Design

1. **Clear Instructions**: Write specific, detailed system prompts
2. **Single Purpose**: Each agent should do one thing well
3. **Tool Selection**: Only add tools the agent needs
4. **Temperature Tuning**: Lower for facts, higher for creativity

### Workflow Design

1. **Modular Steps**: Break complex tasks into small steps
2. **Error Handling**: Add conditions for failure cases
3. **Logging**: Use webhooks to log important events
4. **Testing**: Test with various inputs before production

### Performance

1. **Timeout Settings**: Set appropriate timeouts
2. **Token Limits**: Monitor usage to control costs
3. **Caching**: Use workflows to cache common queries
4. **Rate Limits**: Stay within your plan's limits

### Security

1. **API Key Rotation**: Rotate keys periodically
2. **Least Privilege**: Use minimal required permissions
3. **Audit Logs**: Review team activity regularly
4. **Secure Webhooks**: Use secrets for webhook verification

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open search |
| `Cmd/Ctrl + N` | New agent |
| `Escape` | Close modal |

---

## Getting Help

- **Documentation**: [docs.mimoai.co](https://docs.mimoai.co)
- **API Reference**: [api.mimoai.co/docs](https://api.mimoai.co/docs)
- **Support**: support@gagiteck.com
- **Status**: [status.mimoai.co](https://status.mimoai.co)

---

## FAQ

### How do I reset my password?

Click "Forgot Password" on the login page, or go to Settings > Security.

### Why did my execution fail?

Check the execution details for error messages. Common causes:
- Invalid API credentials
- Timeout exceeded
- Rate limit reached

### Can I export my data?

Yes, use the API to export agents, workflows, and execution history.

### How is usage calculated?

Usage is based on:
- Number of API requests
- Token consumption (input + output)
- Workflow executions

### What models are available?

- Claude 3 Sonnet (default)
- Claude 3 Opus (higher capability)
- Claude 3 Haiku (faster, lower cost)
- GPT-4 (coming soon)
