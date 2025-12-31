"""Tests for agent endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.routes.agents import _agents_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test."""
    _agents_db.clear()
    yield
    _agents_db.clear()


class TestAgentEndpoints:
    """Tests for agent API endpoints."""

    def test_list_agents_empty(self):
        """GET /v1/agents should return empty list initially."""
        response = client.get("/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0

    def test_create_agent(self):
        """POST /v1/agents should create an agent."""
        response = client.post(
            "/v1/agents",
            json={"name": "Test Agent"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["id"].startswith("agent_")
        assert data["status"] == "active"

    def test_create_agent_with_config(self):
        """POST /v1/agents should accept configuration."""
        response = client.post(
            "/v1/agents",
            json={
                "name": "Custom Agent",
                "system_prompt": "You are helpful.",
                "config": {
                    "model": "claude-3-opus",
                    "max_tokens": 2048,
                    "temperature": 0.5,
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["system_prompt"] == "You are helpful."
        assert data["config"]["model"] == "claude-3-opus"
        assert data["config"]["max_tokens"] == 2048

    def test_create_agent_validation(self):
        """POST /v1/agents should validate input."""
        response = client.post(
            "/v1/agents",
            json={"name": ""},  # Empty name
        )
        assert response.status_code == 422

    def test_get_agent(self):
        """GET /v1/agents/{id} should return agent."""
        # Create agent first
        create_response = client.post(
            "/v1/agents",
            json={"name": "Test Agent"},
        )
        agent_id = create_response.json()["id"]

        # Get agent
        response = client.get(f"/v1/agents/{agent_id}")
        assert response.status_code == 200
        assert response.json()["id"] == agent_id

    def test_get_agent_not_found(self):
        """GET /v1/agents/{id} should return 404 for missing agent."""
        response = client.get("/v1/agents/agent_nonexistent")
        assert response.status_code == 404

    def test_update_agent(self):
        """PATCH /v1/agents/{id} should update agent."""
        # Create agent
        create_response = client.post(
            "/v1/agents",
            json={"name": "Original Name"},
        )
        agent_id = create_response.json()["id"]

        # Update agent
        response = client.patch(
            f"/v1/agents/{agent_id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_agent(self):
        """DELETE /v1/agents/{id} should delete agent."""
        # Create agent
        create_response = client.post(
            "/v1/agents",
            json={"name": "To Delete"},
        )
        agent_id = create_response.json()["id"]

        # Delete agent
        response = client.delete(f"/v1/agents/{agent_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/v1/agents/{agent_id}")
        assert get_response.status_code == 404

    def test_run_agent(self):
        """POST /v1/agents/{id}/run should execute agent."""
        # Create agent
        create_response = client.post(
            "/v1/agents",
            json={"name": "Runner Agent"},
        )
        agent_id = create_response.json()["id"]

        # Run agent
        response = client.post(
            f"/v1/agents/{agent_id}/run",
            json={"message": "Hello, agent!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert "content" in data
        assert "usage" in data

    def test_list_agents_pagination(self):
        """GET /v1/agents should support pagination."""
        # Create multiple agents
        for i in range(5):
            client.post("/v1/agents", json={"name": f"Agent {i}"})

        # Get with limit
        response = client.get("/v1/agents?limit=2&offset=0")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5

        # Get next page
        response = client.get("/v1/agents?limit=2&offset=2")
        data = response.json()
        assert len(data["data"]) == 2
