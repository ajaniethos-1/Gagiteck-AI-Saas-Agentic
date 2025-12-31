"""Agent API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()


# --- Models ---

class AgentConfig(BaseModel):
    """Agent configuration."""
    model: str = "claude-3-sonnet"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_iterations: int = 25
    timeout_ms: int = 120000


class AgentCreate(BaseModel):
    """Request to create an agent."""
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: Optional[str] = None
    config: Optional[AgentConfig] = None
    tools: List[str] = []
    metadata: dict = {}


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

@router.get("", response_model=AgentList)
async def list_agents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all agents."""
    agents = list(_agents_db.values())
    return AgentList(
        data=[Agent(**a) for a in agents[offset:offset + limit]],
        total=len(agents),
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=Agent, status_code=201)
async def create_agent(request: AgentCreate):
    """Create a new agent."""
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


@router.get("/{agent_id}", response_model=Agent)
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


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(agent_id: str, request: AgentRunRequest):
    """Run an agent with a message."""
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
