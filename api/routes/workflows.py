"""Workflow API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()


# --- Models ---

class WorkflowStep(BaseModel):
    """A step in a workflow."""
    id: str
    name: str
    agent_id: Optional[str] = None
    action: Optional[str] = None
    input_template: Optional[str] = None
    depends_on: List[str] = []
    condition: Optional[str] = None
    timeout_ms: int = 60000


class WorkflowCreate(BaseModel):
    """Request to create a workflow."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    steps: List[WorkflowStep] = []
    triggers: List[dict] = []
    metadata: dict = {}


class WorkflowUpdate(BaseModel):
    """Request to update a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None
    triggers: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class Workflow(BaseModel):
    """Workflow response model."""
    id: str
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep] = []
    triggers: List[dict] = []
    metadata: dict = {}
    status: str = "active"
    created_at: datetime
    updated_at: datetime


class WorkflowTriggerRequest(BaseModel):
    """Request to trigger a workflow."""
    inputs: dict = {}


class WorkflowRunResponse(BaseModel):
    """Response from workflow trigger."""
    id: str
    workflow_id: str
    status: str
    inputs: dict
    outputs: dict = {}
    started_at: datetime


class WorkflowList(BaseModel):
    """Paginated list of workflows."""
    data: List[Workflow]
    total: int
    limit: int
    offset: int


# --- In-memory storage ---
_workflows_db: dict[str, dict] = {}
_workflow_runs_db: dict[str, dict] = {}


# --- Endpoints ---

@router.get("", response_model=WorkflowList)
async def list_workflows(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all workflows."""
    workflows = list(_workflows_db.values())
    return WorkflowList(
        data=[Workflow(**w) for w in workflows[offset:offset + limit]],
        total=len(workflows),
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=Workflow, status_code=201)
async def create_workflow(request: WorkflowCreate):
    """Create a new workflow."""
    workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    workflow = {
        "id": workflow_id,
        "name": request.name,
        "description": request.description,
        "steps": [s.model_dump() for s in request.steps],
        "triggers": request.triggers,
        "metadata": request.metadata,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    _workflows_db[workflow_id] = workflow
    return Workflow(**workflow)


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get a workflow by ID."""
    if workflow_id not in _workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return Workflow(**_workflows_db[workflow_id])


@router.patch("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, request: WorkflowUpdate):
    """Update a workflow."""
    if workflow_id not in _workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows_db[workflow_id]

    if request.name is not None:
        workflow["name"] = request.name
    if request.description is not None:
        workflow["description"] = request.description
    if request.steps is not None:
        workflow["steps"] = [s.model_dump() for s in request.steps]
    if request.triggers is not None:
        workflow["triggers"] = request.triggers
    if request.metadata is not None:
        workflow["metadata"] = request.metadata

    workflow["updated_at"] = datetime.utcnow()

    return Workflow(**workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    if workflow_id not in _workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    del _workflows_db[workflow_id]


@router.post("/{workflow_id}/trigger", response_model=WorkflowRunResponse)
async def trigger_workflow(workflow_id: str, request: WorkflowTriggerRequest):
    """Trigger a workflow execution."""
    if workflow_id not in _workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    run_id = f"run_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    run = {
        "id": run_id,
        "workflow_id": workflow_id,
        "status": "running",
        "inputs": request.inputs,
        "outputs": {},
        "started_at": now,
    }

    _workflow_runs_db[run_id] = run

    return WorkflowRunResponse(**run)


@router.get("/{workflow_id}/runs", response_model=List[WorkflowRunResponse])
async def list_workflow_runs(workflow_id: str):
    """List runs for a workflow."""
    if workflow_id not in _workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    runs = [
        WorkflowRunResponse(**r)
        for r in _workflow_runs_db.values()
        if r["workflow_id"] == workflow_id
    ]
    return runs
