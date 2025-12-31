"""Tests for workflow endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.routes.workflows import _workflows_db, _workflow_runs_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test."""
    _workflows_db.clear()
    _workflow_runs_db.clear()
    yield
    _workflows_db.clear()
    _workflow_runs_db.clear()


class TestWorkflowEndpoints:
    """Tests for workflow API endpoints."""

    def test_list_workflows_empty(self):
        """GET /v1/workflows should return empty list initially."""
        response = client.get("/v1/workflows")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0

    def test_create_workflow(self):
        """POST /v1/workflows should create a workflow."""
        response = client.post(
            "/v1/workflows",
            json={"name": "Test Workflow"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert data["id"].startswith("wf_")
        assert data["status"] == "active"

    def test_create_workflow_with_steps(self):
        """POST /v1/workflows should accept steps."""
        response = client.post(
            "/v1/workflows",
            json={
                "name": "Multi-Step Workflow",
                "description": "A workflow with multiple steps",
                "steps": [
                    {
                        "id": "step1",
                        "name": "First Step",
                        "agent_id": "agent_123",
                    },
                    {
                        "id": "step2",
                        "name": "Second Step",
                        "agent_id": "agent_456",
                        "depends_on": ["step1"],
                    },
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["steps"]) == 2
        assert data["steps"][1]["depends_on"] == ["step1"]

    def test_get_workflow(self):
        """GET /v1/workflows/{id} should return workflow."""
        # Create workflow
        create_response = client.post(
            "/v1/workflows",
            json={"name": "Test Workflow"},
        )
        workflow_id = create_response.json()["id"]

        # Get workflow
        response = client.get(f"/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        assert response.json()["id"] == workflow_id

    def test_get_workflow_not_found(self):
        """GET /v1/workflows/{id} should return 404 for missing workflow."""
        response = client.get("/v1/workflows/wf_nonexistent")
        assert response.status_code == 404

    def test_update_workflow(self):
        """PATCH /v1/workflows/{id} should update workflow."""
        # Create workflow
        create_response = client.post(
            "/v1/workflows",
            json={"name": "Original Name"},
        )
        workflow_id = create_response.json()["id"]

        # Update workflow
        response = client.patch(
            f"/v1/workflows/{workflow_id}",
            json={
                "name": "Updated Name",
                "description": "New description",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    def test_delete_workflow(self):
        """DELETE /v1/workflows/{id} should delete workflow."""
        # Create workflow
        create_response = client.post(
            "/v1/workflows",
            json={"name": "To Delete"},
        )
        workflow_id = create_response.json()["id"]

        # Delete workflow
        response = client.delete(f"/v1/workflows/{workflow_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/v1/workflows/{workflow_id}")
        assert get_response.status_code == 404

    def test_trigger_workflow(self):
        """POST /v1/workflows/{id}/trigger should start execution."""
        # Create workflow
        create_response = client.post(
            "/v1/workflows",
            json={"name": "Triggerable Workflow"},
        )
        workflow_id = create_response.json()["id"]

        # Trigger workflow
        response = client.post(
            f"/v1/workflows/{workflow_id}/trigger",
            json={"inputs": {"user_id": "123"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert data["status"] == "running"
        assert data["inputs"] == {"user_id": "123"}

    def test_list_workflow_runs(self):
        """GET /v1/workflows/{id}/runs should list executions."""
        # Create workflow
        create_response = client.post(
            "/v1/workflows",
            json={"name": "Workflow With Runs"},
        )
        workflow_id = create_response.json()["id"]

        # Trigger multiple times
        client.post(f"/v1/workflows/{workflow_id}/trigger", json={})
        client.post(f"/v1/workflows/{workflow_id}/trigger", json={})

        # List runs
        response = client.get(f"/v1/workflows/{workflow_id}/runs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
