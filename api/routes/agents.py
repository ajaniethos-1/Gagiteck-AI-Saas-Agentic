"""Agent API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()


# --- Models ---

class AgentConfig(BaseModel):
    """Agent configuration settings."""
    model: str = Field("claude-3-sonnet", description="LLM model to use", examples=["claude-3-sonnet", "claude-3-opus", "gpt-4"])
    max_tokens: int = Field(4096, description="Maximum tokens in response", ge=1, le=100000)
    temperature: float = Field(0.7, description="Sampling temperature", ge=0, le=2)
    max_iterations: int = Field(25, description="Max tool-use iterations", ge=1, le=100)
    timeout_ms: int = Field(120000, description="Request timeout in milliseconds", ge=1000, le=600000)

    model_config = {"json_schema_extra": {"examples": [{"model": "claude-3-sonnet", "max_tokens": 4096, "temperature": 0.7}]}}


class AgentCreate(BaseModel):
    """Request body for creating a new agent."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name", examples=["Customer Support Bot"])
    system_prompt: Optional[str] = Field(None, description="System prompt defining agent behavior", examples=["You are a helpful customer support agent."])
    config: Optional[AgentConfig] = Field(None, description="Agent configuration settings")
    tools: List[str] = Field([], description="List of tool IDs the agent can use", examples=[["search", "calculator"]])
    metadata: dict = Field({}, description="Custom metadata key-value pairs")

    model_config = {"json_schema_extra": {"examples": [{"name": "Support Agent", "system_prompt": "You are a helpful assistant.", "tools": ["search"]}]}}


class AgentUpdate(BaseModel):
    """Request to update an agent."""
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    config: Optional[AgentConfig] = None
    tools: Optional[List[str]] = None
    metadata: Optional[dict] = None


class Agent(BaseModel):
    """Agent response model."""
    id: str
    name: str
    system_prompt: Optional[str] = None
    config: AgentConfig
    tools: List[str] = []
    metadata: dict = {}
    status: str = "active"
    created_at: datetime
    updated_at: datetime


class AgentRunRequest(BaseModel):
    """Request to run an agent."""
    message: str = Field(..., min_length=1)
    context: Optional[dict] = None
    stream: bool = False


class AgentRunResponse(BaseModel):
    """Response from agent run."""
    id: str
    agent_id: str
    content: str
    model: str
    tool_calls: List[dict] = []
    usage: dict = {}
    created_at: datetime


class AgentList(BaseModel):
    """Paginated list of agents."""
    data: List[Agent]
    total: int
    limit: int
    offset: int


# --- In-memory storage (replace with database) ---
_agents_db: dict[str, dict] = {}


# --- Endpoints ---

@router.get(
    "",
    response_model=AgentList,
    summary="List agents",
    description="Retrieve a paginated list of all agents in your account.",
)
async def list_agents(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip"),
):
    """List all agents with pagination support."""
    agents = list(_agents_db.values())
    return AgentList(
        data=[Agent(**a) for a in agents[offset:offset + limit]],
        total=len(agents),
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=Agent,
    status_code=201,
    summary="Create agent",
    description="Create a new AI agent with custom configuration, tools, and system prompt.",
)
async def create_agent(request: AgentCreate):
    """Create a new agent with the specified configuration."""
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    agent = {
        "id": agent_id,
        "name": request.name,
        "system_prompt": request.system_prompt,
        "config": (request.config or AgentConfig()).model_dump(),
        "tools": request.tools,
        "metadata": request.metadata,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    _agents_db[agent_id] = agent
    return Agent(**agent)


@router.get(
    "/{agent_id}",
    response_model=Agent,
    summary="Get agent",
    description="Retrieve a specific agent by its unique identifier.",
    responses={404: {"description": "Agent not found"}},
)
async def get_agent(agent_id: str):
    """Get an agent by ID."""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return Agent(**_agents_db[agent_id])


@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, request: AgentUpdate):
    """Update an agent."""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = _agents_db[agent_id]

    if request.name is not None:
        agent["name"] = request.name
    if request.system_prompt is not None:
        agent["system_prompt"] = request.system_prompt
    if request.config is not None:
        agent["config"] = request.config.model_dump()
    if request.tools is not None:
        agent["tools"] = request.tools
    if request.metadata is not None:
        agent["metadata"] = request.metadata

    agent["updated_at"] = datetime.utcnow()

    return Agent(**agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    del _agents_db[agent_id]


@router.post(
    "/{agent_id}/run",
    response_model=AgentRunResponse,
    summary="Run agent",
    description="Execute an agent with a user message. The agent will process the message using its configured LLM and tools.",
    responses={404: {"description": "Agent not found"}},
)
async def run_agent(agent_id: str, request: AgentRunRequest):
    """Run an agent with a message and return the response."""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = _agents_db[agent_id]

    # Placeholder response - in production, this calls the LLM
    response = AgentRunResponse(
        id=f"run_{uuid.uuid4().hex[:12]}",
        agent_id=agent_id,
        content=f"[Agent '{agent['name']}' processed: {request.message}]",
        model=agent["config"]["model"],
        tool_calls=[],
        usage={"input_tokens": 100, "output_tokens": 50},
        created_at=datetime.utcnow(),
    )

    return response
