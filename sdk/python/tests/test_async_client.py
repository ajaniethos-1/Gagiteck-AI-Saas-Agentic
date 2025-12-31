"""Tests for the async client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from gagiteck import AsyncClient
from gagiteck.exceptions import AuthenticationError, APIError


class TestAsyncClient:
    """Tests for AsyncClient."""

    def test_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(AuthenticationError):
            AsyncClient()

    def test_validates_api_key_format(self):
        """Test that API key format is validated."""
        with pytest.raises(AuthenticationError):
            AsyncClient(api_key="invalid_key")

    def test_accepts_valid_api_key(self):
        """Test that valid API key is accepted."""
        client = AsyncClient(api_key="ggt_test_key_123")
        assert client.api_key == "ggt_test_key_123"

    def test_default_base_url(self):
        """Test default base URL."""
        client = AsyncClient(api_key="ggt_test_key")
        assert client.base_url == "https://api.gagiteck.com/v1"

    def test_custom_base_url(self):
        """Test custom base URL."""
        client = AsyncClient(
            api_key="ggt_test_key",
            base_url="https://custom.api.com/v2/"
        )
        assert client.base_url == "https://custom.api.com/v2"

    def test_has_api_resources(self):
        """Test that client has API resources."""
        client = AsyncClient(api_key="ggt_test_key")
        assert hasattr(client, "agents")
        assert hasattr(client, "workflows")
        assert hasattr(client, "executions")


class TestAsyncAgentsAPI:
    """Tests for AsyncAgentsAPI."""

    @pytest.fixture
    def client(self):
        return AsyncClient(api_key="ggt_test_key")

    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        """Test listing agents."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": [], "total": 0}
            result = await client.agents.list()
            mock_request.assert_called_once_with(
                "GET",
                "/agents",
                params={"limit": 20, "offset": 0}
            )
            assert result == {"data": [], "total": 0}

    @pytest.mark.asyncio
    async def test_get_agent(self, client):
        """Test getting an agent."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "agent_123", "name": "Test"}
            result = await client.agents.get("agent_123")
            mock_request.assert_called_once_with("GET", "/agents/agent_123")
            assert result["id"] == "agent_123"

    @pytest.mark.asyncio
    async def test_create_agent(self, client):
        """Test creating an agent."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "agent_new", "name": "New Agent"}
            result = await client.agents.create(
                name="New Agent",
                model="claude-3-opus",
                system_prompt="You are helpful."
            )
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/agents"
            assert call_args[1]["json"]["name"] == "New Agent"

    @pytest.mark.asyncio
    async def test_run_agent(self, client):
        """Test running an agent."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "run_123", "content": "Hello!"}
            result = await client.agents.run("agent_123", "Hello")
            mock_request.assert_called_once()
            assert result["content"] == "Hello!"


class TestAsyncWorkflowsAPI:
    """Tests for AsyncWorkflowsAPI."""

    @pytest.fixture
    def client(self):
        return AsyncClient(api_key="ggt_test_key")

    @pytest.mark.asyncio
    async def test_list_workflows(self, client):
        """Test listing workflows."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": [], "total": 0}
            result = await client.workflows.list()
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_workflow(self, client):
        """Test triggering a workflow."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "exec_123", "status": "running"}
            result = await client.workflows.trigger("wf_123", inputs={"key": "value"})
            mock_request.assert_called_once()
            assert result["status"] == "running"


class TestAsyncExecutionsAPI:
    """Tests for AsyncExecutionsAPI."""

    @pytest.fixture
    def client(self):
        return AsyncClient(api_key="ggt_test_key")

    @pytest.mark.asyncio
    async def test_get_execution(self, client):
        """Test getting an execution."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "exec_123", "status": "completed"}
            result = await client.executions.get("exec_123")
            mock_request.assert_called_once_with("GET", "/executions/exec_123")

    @pytest.mark.asyncio
    async def test_cancel_execution(self, client):
        """Test cancelling an execution."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": "exec_123", "status": "cancelled"}
            result = await client.executions.cancel("exec_123")
            mock_request.assert_called_once()
            assert result["status"] == "cancelled"


class TestAsyncClientContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with AsyncClient(api_key="ggt_test_key") as client:
            assert client.api_key == "ggt_test_key"
