"""Tests for workflow models and engine."""

import pytest
from gagiteck.workflows.models import (
    Workflow,
    WorkflowStep,
    WorkflowRun,
    WorkflowStatus,
    StepStatus,
    StepResult,
)


class TestWorkflowStep:
    """Tests for WorkflowStep."""

    def test_step_creation(self):
        """Step should be created with required fields."""
        step = WorkflowStep(
            id="step1",
            name="First Step",
        )
        assert step.id == "step1"
        assert step.name == "First Step"
        assert step.depends_on == []

    def test_step_with_dependencies(self):
        """Step should support dependencies."""
        step = WorkflowStep(
            id="step2",
            name="Second Step",
            depends_on=["step1"],
        )
        assert step.depends_on == ["step1"]


class TestWorkflow:
    """Tests for Workflow class."""

    def test_workflow_auto_generates_id(self):
        """Workflow should auto-generate ID."""
        workflow = Workflow(name="Test")
        assert workflow.id is not None
        assert workflow.id.startswith("wf_")

    def test_workflow_add_step(self):
        """Workflow should allow adding steps."""
        workflow = Workflow(name="Test")
        step = WorkflowStep(id="step1", name="Step 1")

        workflow.add_step(step)
        assert len(workflow.steps) == 1

    def test_workflow_get_step(self):
        """Workflow should retrieve step by ID."""
        step = WorkflowStep(id="step1", name="Step 1")
        workflow = Workflow(name="Test", steps=[step])

        found = workflow.get_step("step1")
        assert found is not None
        assert found.name == "Step 1"

    def test_workflow_get_step_not_found(self):
        """Workflow should return None for missing step."""
        workflow = Workflow(name="Test")
        assert workflow.get_step("nonexistent") is None

    def test_execution_order_simple(self):
        """Workflow should determine simple execution order."""
        workflow = Workflow(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A"),
                WorkflowStep(id="b", name="B"),
            ],
        )

        order = workflow.get_execution_order()
        assert len(order) == 1
        assert set(order[0]) == {"a", "b"}

    def test_execution_order_sequential(self):
        """Workflow should determine sequential execution order."""
        workflow = Workflow(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A"),
                WorkflowStep(id="b", name="B", depends_on=["a"]),
                WorkflowStep(id="c", name="C", depends_on=["b"]),
            ],
        )

        order = workflow.get_execution_order()
        assert len(order) == 3
        assert order[0] == ["a"]
        assert order[1] == ["b"]
        assert order[2] == ["c"]

    def test_execution_order_parallel(self):
        """Workflow should identify parallel steps."""
        workflow = Workflow(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A"),
                WorkflowStep(id="b", name="B", depends_on=["a"]),
                WorkflowStep(id="c", name="C", depends_on=["a"]),
                WorkflowStep(id="d", name="D", depends_on=["b", "c"]),
            ],
        )

        order = workflow.get_execution_order()
        assert len(order) == 3
        assert order[0] == ["a"]
        assert set(order[1]) == {"b", "c"}
        assert order[2] == ["d"]

    def test_execution_order_circular_dependency(self):
        """Workflow should detect circular dependencies."""
        workflow = Workflow(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A", depends_on=["c"]),
                WorkflowStep(id="b", name="B", depends_on=["a"]),
                WorkflowStep(id="c", name="C", depends_on=["b"]),
            ],
        )

        with pytest.raises(ValueError, match="Circular dependency"):
            workflow.get_execution_order()


class TestWorkflowRun:
    """Tests for WorkflowRun."""

    def test_run_auto_generates_id(self):
        """Run should auto-generate ID."""
        run = WorkflowRun(workflow_id="wf_123")
        assert run.id is not None
        assert run.id.startswith("run_")

    def test_run_default_status(self):
        """Run should start as pending."""
        run = WorkflowRun(workflow_id="wf_123")
        assert run.status == WorkflowStatus.PENDING

    def test_run_get_step_result(self):
        """Run should retrieve step result by ID."""
        result = StepResult(step_id="step1", status=StepStatus.COMPLETED)
        run = WorkflowRun(
            workflow_id="wf_123",
            step_results=[result],
        )

        found = run.get_step_result("step1")
        assert found is not None
        assert found.status == StepStatus.COMPLETED

    def test_run_duration(self):
        """Run should calculate duration."""
        from datetime import datetime, timedelta

        start = datetime.utcnow()
        end = start + timedelta(seconds=5)

        run = WorkflowRun(
            workflow_id="wf_123",
            started_at=start,
            completed_at=end,
        )

        assert run.duration_ms >= 5000
