"""Tests for execution endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from api.main import app
from api.routes.executions import _executions_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test."""
    _executions_db.clear()
    yield
    _executions_db.clear()


@pytest.fixture
def sample_execution():
    """Create a sample execution."""
    execution = {
        "id": "run_test123",
        "workflow_id": "wf_123",
        "status": "running",
        "inputs": {"key": "value"},
        "outputs": {},
        "step_results": [],
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "duration_ms": 0,
    }
    _executions_db["run_test123"] = execution
    return execution


class TestExecutionEndpoints:
    """Tests for execution API endpoints."""

    def test_list_executions_empty(self):
        """GET /v1/executions should return empty list initially."""
        response = client.get("/v1/executions")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0

    def test_list_executions_with_data(self, sample_execution):
        """GET /v1/executions should return executions."""
        response = client.get("/v1/executions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["id"] == "run_test123"

    def test_list_executions_filter_by_status(self, sample_execution):
        """GET /v1/executions should filter by status."""
        # Add completed execution
        _executions_db["run_completed"] = {
            "id": "run_completed",
            "workflow_id": "wf_456",
            "status": "completed",
            "inputs": {},
            "outputs": {},
            "step_results": [],
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "duration_ms": 1000,
        }

        # Filter running
        response = client.get("/v1/executions?status=running")
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["status"] == "running"

        # Filter completed
        response = client.get("/v1/executions?status=completed")
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["status"] == "completed"

    def test_get_execution(self, sample_execution):
        """GET /v1/executions/{id} should return execution."""
        response = client.get("/v1/executions/run_test123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "run_test123"
        assert data["workflow_id"] == "wf_123"

    def test_get_execution_not_found(self):
        """GET /v1/executions/{id} should return 404 for missing execution."""
        response = client.get("/v1/executions/run_nonexistent")
        assert response.status_code == 404

    def test_cancel_execution(self, sample_execution):
        """POST /v1/executions/{id}/cancel should cancel execution."""
        response = client.post("/v1/executions/run_test123/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["completed_at"] is not None

    def test_cancel_execution_not_found(self):
        """POST /v1/executions/{id}/cancel should return 404 for missing."""
        response = client.post("/v1/executions/run_nonexistent/cancel")
        assert response.status_code == 404

    def test_cancel_completed_execution_fails(self, sample_execution):
        """POST /v1/executions/{id}/cancel should fail for completed."""
        # Mark as completed
        _executions_db["run_test123"]["status"] = "completed"

        response = client.post("/v1/executions/run_test123/cancel")
        assert response.status_code == 400
        assert "Cannot cancel" in response.json()["detail"]

    def test_get_execution_logs(self, sample_execution):
        """GET /v1/executions/{id}/logs should return logs."""
        response = client.get("/v1/executions/run_test123/logs")
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == "run_test123"
        assert "logs" in data
        assert len(data["logs"]) > 0

    def test_list_executions_pagination(self):
        """GET /v1/executions should support pagination."""
        # Create multiple executions
        for i in range(5):
            _executions_db[f"run_{i}"] = {
                "id": f"run_{i}",
                "workflow_id": "wf_test",
                "status": "completed",
                "inputs": {},
                "outputs": {},
                "step_results": [],
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "duration_ms": 100,
            }

        # Get with limit
        response = client.get("/v1/executions?limit=2&offset=0")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
