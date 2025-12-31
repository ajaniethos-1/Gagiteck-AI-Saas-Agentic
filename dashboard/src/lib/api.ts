/**
 * Gagiteck API Client for Dashboard
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(error.detail || 'Request failed', response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// --- Types ---

export interface AgentConfig {
  model: string;
  max_tokens: number;
  temperature: number;
  max_iterations: number;
  timeout_ms: number;
}

export interface Agent {
  id: string;
  name: string;
  system_prompt: string | null;
  config: AgentConfig;
  tools: string[];
  metadata: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AgentList {
  data: Agent[];
  total: number;
  limit: number;
  offset: number;
}

export interface AgentCreate {
  name: string;
  system_prompt?: string;
  config?: Partial<AgentConfig>;
  tools?: string[];
  metadata?: Record<string, any>;
}

export interface AgentRunRequest {
  message: string;
  context?: Record<string, any>;
  stream?: boolean;
}

export interface AgentRunResponse {
  id: string;
  agent_id: string;
  content: string;
  model: string;
  tool_calls: any[];
  usage: Record<string, number>;
  created_at: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string | null;
  steps: any[];
  metadata: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface WorkflowList {
  data: Workflow[];
  total: number;
  limit: number;
  offset: number;
}

export interface Execution {
  id: string;
  type: string;
  resource_id: string;
  status: string;
  result: any;
  error: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface ExecutionList {
  data: Execution[];
  total: number;
  limit: number;
  offset: number;
}

// --- API Functions ---

export const api = {
  // Health
  async health() {
    return request<{ status: string; version: string }>('/health');
  },

  // Agents
  agents: {
    async list(limit = 20, offset = 0): Promise<AgentList> {
      return request(`/v1/agents?limit=${limit}&offset=${offset}`);
    },

    async get(id: string): Promise<Agent> {
      return request(`/v1/agents/${id}`);
    },

    async create(data: AgentCreate): Promise<Agent> {
      return request('/v1/agents', { method: 'POST', body: data });
    },

    async update(id: string, data: Partial<AgentCreate>): Promise<Agent> {
      return request(`/v1/agents/${id}`, { method: 'PATCH', body: data });
    },

    async delete(id: string): Promise<void> {
      return request(`/v1/agents/${id}`, { method: 'DELETE' });
    },

    async run(id: string, data: AgentRunRequest): Promise<AgentRunResponse> {
      return request(`/v1/agents/${id}/run`, { method: 'POST', body: data });
    },
  },

  // Workflows
  workflows: {
    async list(limit = 20, offset = 0): Promise<WorkflowList> {
      return request(`/v1/workflows?limit=${limit}&offset=${offset}`);
    },

    async get(id: string): Promise<Workflow> {
      return request(`/v1/workflows/${id}`);
    },

    async create(data: { name: string; description?: string; steps?: any[] }): Promise<Workflow> {
      return request('/v1/workflows', { method: 'POST', body: data });
    },

    async update(id: string, data: Partial<{ name: string; description: string; steps: any[] }>): Promise<Workflow> {
      return request(`/v1/workflows/${id}`, { method: 'PATCH', body: data });
    },

    async delete(id: string): Promise<void> {
      return request(`/v1/workflows/${id}`, { method: 'DELETE' });
    },

    async trigger(id: string, input?: Record<string, any>): Promise<Execution> {
      return request(`/v1/workflows/${id}/trigger`, { method: 'POST', body: { input } });
    },
  },

  // Executions
  executions: {
    async list(limit = 20, offset = 0): Promise<ExecutionList> {
      return request(`/v1/executions?limit=${limit}&offset=${offset}`);
    },

    async get(id: string): Promise<Execution> {
      return request(`/v1/executions/${id}`);
    },

    async cancel(id: string): Promise<Execution> {
      return request(`/v1/executions/${id}/cancel`, { method: 'POST' });
    },
  },
};

export { ApiError };
