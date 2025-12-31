"""Execution API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# --- Models ---

class StepResult(BaseModel):
    """Result of a workflow step."""
    step_id: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


class Execution(BaseModel):
    """Execution response model."""
    id: str
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: str
    inputs: dict = {}
    outputs: dict = {}
    step_results: List[StepResult] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


class ExecutionList(BaseModel):
    """Paginated list of executions."""
    data: List[Execution]
    total: int
    limit: int
    offset: int


# --- In-memory storage ---
_executions_db: dict[str, dict] = {}


# --- Endpoints ---

@router.get("", response_model=ExecutionList)
async def list_executions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
):
    """List all executions."""
    executions = list(_executions_db.values())

    if status:
        executions = [e for e in executions if e["status"] == status]

    return ExecutionList(
        data=[Execution(**e) for e in executions[offset:offset + limit]],
        total=len(executions),
        limit=limit,
        offset=offset,
    )


@router.get("/{execution_id}", response_model=Execution)
async def get_execution(execution_id: str):
    """Get an execution by ID."""
    if execution_id not in _executions_db:
        raise HTTPException(status_code=404, detail="Execution not found")
    return Execution(**_executions_db[execution_id])


@router.post("/{execution_id}/cancel", response_model=Execution)
async def cancel_execution(execution_id: str):
    """Cancel a running execution."""
    if execution_id not in _executions_db:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = _executions_db[execution_id]

    if execution["status"] not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel execution with status: {execution['status']}"
        )

    execution["status"] = "cancelled"
    execution["completed_at"] = datetime.utcnow()

    return Execution(**execution)


@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str):
    """Get logs for an execution."""
    if execution_id not in _executions_db:
        raise HTTPException(status_code=404, detail="Execution not found")

    # Placeholder - in production, fetch from logging service
    return {
        "execution_id": execution_id,
        "logs": [
            {"timestamp": datetime.utcnow().isoformat(), "level": "info", "message": "Execution started"},
            {"timestamp": datetime.utcnow().isoformat(), "level": "info", "message": "Processing..."},
        ]
    }
