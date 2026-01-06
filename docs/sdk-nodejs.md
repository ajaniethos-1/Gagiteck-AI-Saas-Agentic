# Node.js SDK Guide

Official Node.js/TypeScript client library for the Gagiteck AI SaaS Platform.

## Installation

```bash
npm install @gagiteck/sdk
```

Or with yarn/pnpm:

```bash
yarn add @gagiteck/sdk
pnpm add @gagiteck/sdk
```

## Quick Start

### API Client

```typescript
import { GagiteckClient } from '@gagiteck/sdk';

// Initialize the client
const client = new GagiteckClient({
  apiKey: 'ggt_your_api_key'
});

// List all agents
const agents = await client.agents.list();
console.log(`Found ${agents.data.length} agents`);

// Create an agent
const agent = await client.agents.create({
  name: 'Customer Support Bot',
  systemPrompt: 'You are a helpful customer support agent.',
  config: { model: 'claude-3-sonnet' }
});

// Run an agent
const response = await client.agents.run({
  agentId: agent.id,
  message: 'How do I reset my password?'
});
console.log(response.content);
```

### Local Agents

```typescript
import { Agent, defineTool } from '@gagiteck/sdk';

// Define custom tools
const searchKnowledgeBase = defineTool({
  name: 'searchKnowledgeBase',
  description: 'Search the knowledge base for answers',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query' }
    },
    required: ['query']
  },
  execute: async ({ query }) => {
    // Implementation here
    return `Found answer for: ${query}`;
  }
});

// Create an agent with tools
const agent = new Agent({
  name: 'Support Agent',
  model: 'claude-3-opus',
  systemPrompt: 'You are a customer support agent.',
  tools: [searchKnowledgeBase],
  memoryEnabled: true
});

// Run the agent
const response = await agent.run('I need help with billing');
console.log(response.text);
```

## Client Configuration

```typescript
import { GagiteckClient } from '@gagiteck/sdk';

const client = new GagiteckClient({
  apiKey: 'ggt_your_api_key',      // Required: API key
  baseUrl: 'https://api.custom.com', // Optional: Custom API URL
  timeout: 60000,                    // Optional: Request timeout (default: 30000)
  maxRetries: 3,                     // Optional: Retry count (default: 3)
  debug: true,                       // Optional: Enable debug logging
});
```

### Environment Variables

```bash
export GAGITECK_API_KEY="ggt_your_api_key"
export GAGITECK_BASE_URL="https://api.gagiteck.com"
```

```typescript
import { GagiteckClient } from '@gagiteck/sdk';

// Client will automatically use environment variables
const client = new GagiteckClient();
```

## Agents API

### List Agents

```typescript
// List all agents
const agents = await client.agents.list();

// With pagination
const agents = await client.agents.list({
  limit: 10,
  offset: 0
});

// Filter by status
const activeAgents = await client.agents.list({
  status: 'active'
});
```

### Create Agent

```typescript
const agent = await client.agents.create({
  name: 'Research Assistant',
  systemPrompt: 'You are a research assistant.',
  config: {
    model: 'claude-3-sonnet',
    maxTokens: 4096,
    temperature: 0.7
  },
  tools: ['web_search', 'document_reader'],
  metadata: { department: 'research' }
});
```

### Get Agent

```typescript
const agent = await client.agents.get('agent_123');
console.log(`Name: ${agent.name}`);
console.log(`Status: ${agent.status}`);
```

### Update Agent

```typescript
const agent = await client.agents.update('agent_123', {
  name: 'Updated Name',
  config: { temperature: 0.5 }
});
```

### Delete Agent

```typescript
await client.agents.delete('agent_123');
```

### Run Agent

```typescript
// Simple run
const response = await client.agents.run({
  agentId: 'agent_123',
  message: 'Hello, how can you help?'
});

// With conversation context
const response = await client.agents.run({
  agentId: 'agent_123',
  message: 'Tell me more',
  conversationId: 'conv_456'
});

// With streaming
const stream = await client.agents.runStream({
  agentId: 'agent_123',
  message: 'Write a long story'
});

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```

## Workflows API

### Create Workflow

```typescript
const workflow = await client.workflows.create({
  name: 'Data Processing Pipeline',
  description: 'Process and analyze data',
  steps: [
    {
      id: 'extract',
      name: 'Extract Data',
      agentId: 'agent_extractor'
    },
    {
      id: 'transform',
      name: 'Transform Data',
      agentId: 'agent_transformer',
      dependsOn: ['extract']
    },
    {
      id: 'load',
      name: 'Load Data',
      agentId: 'agent_loader',
      dependsOn: ['transform']
    }
  ]
});
```

### Trigger Workflow

```typescript
const run = await client.workflows.trigger({
  workflowId: 'wf_123',
  inputs: {
    source: 'database',
    destination: 'warehouse'
  }
});
console.log(`Run ID: ${run.id}`);
console.log(`Status: ${run.status}`);
```

### Get Workflow Run

```typescript
const run = await client.workflows.getRun({
  workflowId: 'wf_123',
  runId: 'run_456'
});

for (const step of run.steps) {
  console.log(`  ${step.name}: ${step.status}`);
}
```

## Custom Tools

### Basic Tool

```typescript
import { defineTool } from '@gagiteck/sdk';

const calculateSum = defineTool({
  name: 'calculateSum',
  description: 'Add two numbers together',
  parameters: {
    type: 'object',
    properties: {
      a: { type: 'number' },
      b: { type: 'number' }
    },
    required: ['a', 'b']
  },
  execute: async ({ a, b }) => a + b
});
```

### Tool with Complex Types

```typescript
import { defineTool } from '@gagiteck/sdk';

interface Product {
  name: string;
  price: number;
  category: string;
}

const searchProducts = defineTool({
  name: 'searchProducts',
  description: 'Search for products in the catalog',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query' },
      category: { type: 'string', description: 'Optional category filter' },
      limit: { type: 'number', description: 'Max results', default: 10 }
    },
    required: ['query']
  },
  execute: async ({ query, category, limit }): Promise<Product[]> => {
    // Implementation
    return [{ name: 'Product', price: 99.99, category: 'electronics' }];
  }
});
```

### Async Tools with External APIs

```typescript
import { defineTool } from '@gagiteck/sdk';
import axios from 'axios';

const fetchWeather = defineTool({
  name: 'fetchWeather',
  description: 'Fetch current weather for a city',
  parameters: {
    type: 'object',
    properties: {
      city: { type: 'string' }
    },
    required: ['city']
  },
  execute: async ({ city }) => {
    const response = await axios.get(
      `https://api.weather.com/current/${city}`
    );
    return response.data;
  }
});
```

## Error Handling

```typescript
import {
  GagiteckClient,
  GagiteckError,
  AuthenticationError,
  RateLimitError,
  APIError,
  ValidationError
} from '@gagiteck/sdk';

const client = new GagiteckClient({ apiKey: 'ggt_your_key' });

try {
  const response = await client.agents.run({
    agentId: 'agent_123',
    message: 'Hello'
  });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log('Invalid API key');
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after ${error.retryAfter} seconds`);
  } else if (error instanceof ValidationError) {
    console.log(`Invalid request: ${error.details}`);
  } else if (error instanceof APIError) {
    console.log(`API error ${error.statusCode}: ${error.message}`);
  } else if (error instanceof GagiteckError) {
    console.log(`Unexpected error: ${error.message}`);
  }
}
```

## TypeScript Support

The SDK is written in TypeScript and provides full type definitions:

```typescript
import {
  GagiteckClient,
  Agent,
  AgentConfig,
  Workflow,
  WorkflowRun,
  Tool
} from '@gagiteck/sdk';

const client = new GagiteckClient({ apiKey: 'ggt_key' });

// Full type inference
const agent: Agent = await client.agents.get('agent_123');
const config: AgentConfig = agent.config;
```

## Express.js Integration

```typescript
import express from 'express';
import { GagiteckClient } from '@gagiteck/sdk';

const app = express();
const client = new GagiteckClient();

app.post('/api/chat', async (req, res) => {
  const { agentId, message, conversationId } = req.body;

  try {
    const response = await client.agents.run({
      agentId,
      message,
      conversationId
    });

    res.json({
      content: response.content,
      conversationId: response.conversationId
    });
  } catch (error) {
    res.status(500).json({ error: 'Chat failed' });
  }
});

app.listen(3000);
```

## Next.js Integration

```typescript
// app/api/agents/[id]/route.ts
import { GagiteckClient } from '@gagiteck/sdk';
import { NextResponse } from 'next/server';

const client = new GagiteckClient();

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const { message } = await request.json();

  const response = await client.agents.run({
    agentId: params.id,
    message
  });

  return NextResponse.json(response);
}
```

## Examples

### Chatbot with Memory

```typescript
import { Agent } from '@gagiteck/sdk';
import * as readline from 'readline';

const agent = new Agent({
  name: 'Chatbot',
  model: 'claude-3-sonnet',
  memoryEnabled: true,
  systemPrompt: 'You are a friendly chatbot.'
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function chat() {
  rl.question('You: ', async (input) => {
    if (input.toLowerCase() === 'quit') {
      rl.close();
      return;
    }

    const response = await agent.run(input);
    console.log(`Bot: ${response.text}`);
    chat();
  });
}

chat();
```

### RAG Agent

```typescript
import { Agent, defineTool } from '@gagiteck/sdk';
import { ChromaClient } from 'chromadb';

// Setup vector store
const chroma = new ChromaClient();
const collection = await chroma.createCollection({ name: 'docs' });

const searchDocuments = defineTool({
  name: 'searchDocuments',
  description: 'Search documents for relevant information',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string' }
    },
    required: ['query']
  },
  execute: async ({ query }) => {
    const results = await collection.query({
      queryTexts: [query],
      nResults: 5
    });
    return results.documents[0];
  }
});

const agent = new Agent({
  name: 'RAG Agent',
  model: 'claude-3-opus',
  tools: [searchDocuments],
  systemPrompt: `You are a helpful assistant.
    Use the searchDocuments tool to find information.`
});

const response = await agent.run('What is our refund policy?');
console.log(response.text);
```

## Best Practices

1. **Use Environment Variables**: Store API keys in environment variables
2. **Handle Errors**: Always wrap API calls in try/catch
3. **Use TypeScript**: Get full type safety and IDE support
4. **Enable Memory**: Use memoryEnabled for conversational agents
5. **Define Tool Types**: Add proper type definitions to tools

## Resources

- [API Reference](api-reference.md)
- [GitHub Repository](https://github.com/ajaniethos-1/gagiteck-node)
- [npm Package](https://www.npmjs.com/package/@gagiteck/sdk)
- [Examples](https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic/tree/main/examples)
