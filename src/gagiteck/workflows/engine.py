"""Workflow execution engine."""

from typing import Any, Dict, Optional
from datetime import datetime
import asyncio

from gagiteck.workflows.models import (
    Workflow,
    WorkflowRun,
    WorkflowStatus,
    StepResult,
    StepStatus,
)
from gagiteck.agents.runner import AgentRunner


class WorkflowEngine:
    """Engine for executing workflows.

    Handles workflow execution, step orchestration,
    and error handling.

    Example:
        >>> engine = WorkflowEngine()
        >>> run = await engine.run(workflow, inputs={"user_id": "123"})
        >>> print(run.status)
    """

    def __init__(
        self,
        agent_runner: Optional[AgentRunner] = None,
        max_parallel_steps: int = 5,
    ):
        self.agent_runner = agent_runner or AgentRunner()
        self.max_parallel_steps = max_parallel_steps
        self._active_runs: Dict[str, WorkflowRun] = {}

    async def run(
        self,
        workflow: Workflow,
        inputs: Optional[Dict] = None,
    ) -> WorkflowRun:
        """Execute a workflow.

        Args:
            workflow: The workflow to execute
            inputs: Input values for the workflow

        Returns:
            WorkflowRun with results
        """
        run = WorkflowRun(
            workflow_id=workflow.id,
            inputs=inputs or {},
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self._active_runs[run.id] = run

        try:
            # Get execution order
            execution_order = workflow.get_execution_order()

            # Execute steps in order
            step_outputs: Dict[str, Any] = {}

            for step_group in execution_order:
                # Run steps in parallel
                tasks = []
                for step_id in step_group:
                    step = workflow.get_step(step_id)
                    if step:
                        task = self._execute_step(
                            run=run,
                            step=step,
                            inputs=inputs,
                            step_outputs=step_outputs,
                        )
                        tasks.append(task)

                # Wait for all steps in group
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        run.status = WorkflowStatus.FAILED
                        run.error = str(result)
                        break
                    if isinstance(result, StepResult):
                        run.step_results.append(result)
                        if result.status == StepStatus.COMPLETED:
                            step_outputs[result.step_id] = result.output
                        elif result.status == StepStatus.FAILED:
                            run.status = WorkflowStatus.FAILED
                            run.error = result.error
                            break

                if run.status == WorkflowStatus.FAILED:
                    break

            if run.status == WorkflowStatus.RUNNING:
                run.status = WorkflowStatus.COMPLETED
                run.outputs = step_outputs

        except Exception as e:
            run.status = WorkflowStatus.FAILED
            run.error = str(e)

        finally:
            run.completed_at = datetime.utcnow()
            self._active_runs.pop(run.id, None)

        return run

    async def _execute_step(
        self,
        run: WorkflowRun,
        step,
        inputs: Optional[Dict],
        step_outputs: Dict[str, Any],
    ) -> StepResult:
        """Execute a single workflow step."""
        result = StepResult(
            step_id=step.id,
            status=StepStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        try:
            # Check condition if present
            if step.condition:
                if not self._evaluate_condition(step.condition, inputs, step_outputs):
                    result.status = StepStatus.SKIPPED
                    return result

            # Build step input from template
            step_input = self._render_template(
                step.input_template or "",
                inputs=inputs,
                steps=step_outputs,
            )

            # Execute the step
            # In production, this would call the agent
            result.output = f"[Step '{step.name}' executed with input: {step_input}]"
            result.status = StepStatus.COMPLETED

        except Exception as e:
            result.status = StepStatus.FAILED
            result.error = str(e)

        finally:
            result.completed_at = datetime.utcnow()
            if result.started_at:
                result.duration_ms = int(
                    (result.completed_at - result.started_at).total_seconds() * 1000
                )

        return result

    def _evaluate_condition(
        self,
        condition: str,
        inputs: Optional[Dict],
        step_outputs: Dict[str, Any],
    ) -> bool:
        """Evaluate a step condition."""
        # Simple condition evaluation
        # In production, use a safe expression evaluator
        context = {
            "inputs": inputs or {},
            "steps": step_outputs,
        }
        try:
            return bool(eval(condition, {"__builtins__": {}}, context))
        except Exception:
            return True

    def _render_template(
        self,
        template: str,
        inputs: Optional[Dict],
        steps: Dict[str, Any],
    ) -> str:
        """Render a template with variables."""
        result = template

        # Replace {{inputs.key}} patterns
        if inputs:
            for key, value in inputs.items():
                result = result.replace(f"{{{{inputs.{key}}}}}", str(value))

        # Replace {{steps.step_id.output}} patterns
        for step_id, output in steps.items():
            result = result.replace(f"{{{{steps.{step_id}.output}}}}", str(output))

        return result

    async def cancel(self, run_id: str) -> bool:
        """Cancel a running workflow."""
        if run_id in self._active_runs:
            run = self._active_runs[run_id]
            run.status = WorkflowStatus.CANCELLED
            run.completed_at = datetime.utcnow()
            return True
        return False

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Get an active run by ID."""
        return self._active_runs.get(run_id)
