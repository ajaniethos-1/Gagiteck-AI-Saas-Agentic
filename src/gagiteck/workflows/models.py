"""Workflow data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class WorkflowStatus(Enum):
    """Workflow run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A step in a workflow.

    Attributes:
        id: Unique step identifier
        name: Human-readable name
        agent_id: Agent to execute this step
        action: Action to perform
        input_template: Template for step input
        depends_on: List of step IDs this depends on
        condition: Optional condition expression
    """
    id: str
    name: str
    agent_id: Optional[str] = None
    action: Optional[str] = None
    input_template: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout_ms: int = 60000
    retry_count: int = 0
    metadata: Dict = field(default_factory=dict)


@dataclass
class StepResult:
    """Result of a step execution."""
    step_id: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


@dataclass
class Workflow:
    """A workflow definition.

    Workflows orchestrate multiple agents to complete
    complex, multi-step tasks.

    Attributes:
        id: Unique workflow identifier
        name: Human-readable name
        description: What the workflow does
        steps: List of workflow steps
        triggers: Events that trigger the workflow

    Example:
        >>> workflow = Workflow(
        ...     name="Customer Onboarding",
        ...     steps=[
        ...         WorkflowStep(id="verify", name="Verify Email", agent_id="verifier"),
        ...         WorkflowStep(id="setup", name="Setup Account", agent_id="provisioner", depends_on=["verify"]),
        ...     ],
        ... )
    """
    id: Optional[str] = None
    name: str = "Workflow"
    description: Optional[str] = None
    steps: List[WorkflowStep] = field(default_factory=list)
    triggers: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.id is None:
            self.id = f"wf_{uuid.uuid4().hex[:12]}"

    def add_step(self, step: WorkflowStep) -> "Workflow":
        """Add a step to the workflow."""
        self.steps.append(step)
        return self

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        return next((s for s in self.steps if s.id == step_id), None)

    def get_execution_order(self) -> List[List[str]]:
        """Get steps grouped by execution order.

        Returns steps that can run in parallel grouped together.
        """
        # Build dependency graph
        remaining = {s.id for s in self.steps}
        completed = set()
        order = []

        while remaining:
            # Find steps with all dependencies met
            ready = []
            for step in self.steps:
                if step.id not in remaining:
                    continue
                if all(dep in completed for dep in step.depends_on):
                    ready.append(step.id)

            if not ready:
                raise ValueError("Circular dependency detected in workflow")

            order.append(ready)
            completed.update(ready)
            remaining -= set(ready)

        return order


@dataclass
class WorkflowRun:
    """A workflow execution instance."""
    id: Optional[str] = None
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    inputs: Dict = field(default_factory=dict)
    outputs: Dict = field(default_factory=dict)
    step_results: List[StepResult] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"run_{uuid.uuid4().hex[:12]}"

    def get_step_result(self, step_id: str) -> Optional[StepResult]:
        """Get result for a specific step."""
        return next((r for r in self.step_results if r.step_id == step_id), None)

    @property
    def duration_ms(self) -> int:
        """Get total run duration."""
        if not self.started_at:
            return 0
        end = self.completed_at or datetime.utcnow()
        return int((end - self.started_at).total_seconds() * 1000)
