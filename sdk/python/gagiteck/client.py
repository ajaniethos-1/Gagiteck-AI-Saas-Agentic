"""Gagiteck API Client."""

from typing import Optional
import httpx

from gagiteck.exceptions import AuthenticationError, APIError


class Client:
    """Main client for interacting with the Gagiteck API.

    Args:
        api_key: Your Gagiteck API key (starts with 'ggt_')
        base_url: API base URL (default: https://api.gagiteck.com/v1)
        timeout: Request timeout in seconds (default: 30)
        debug: Enable debug logging (default: False)

    Example:
        >>> from gagiteck import Client
        >>> client = Client(api_key="ggt_your_key_here")
        >>> agents = client.agents.list()
    """

    DEFAULT_BASE_URL = "https://api.gagiteck.com/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        debug: bool = False,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        if not api_key.startswith("ggt_"):
            raise AuthenticationError("Invalid API key format. Key should start with 'ggt_'")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.debug = debug

        self._http_client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"gagiteck-python/0.1.0",
            },
            timeout=timeout,
        )

        # Initialize API resources
        self.agents = AgentsAPI(self)
        self.workflows = WorkflowsAPI(self)
        self.executions = ExecutionsAPI(self)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make an HTTP request to the API."""
        try:
            response = self._http_client.request(
                method=method,
                url=path,
                json=json,
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")
            raise APIError(
                code=e.response.status_code,
                message=e.response.text,
            )
        except httpx.RequestError as e:
            raise APIError(code=0, message=str(e))

    def close(self) -> None:
        """Close the HTTP client."""
        self._http_client.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class AgentsAPI:
    """API for managing agents."""

    def __init__(self, client: Client):
        self._client = client

    def list(self, limit: int = 20, offset: int = 0) -> dict:
        """List all agents."""
        return self._client._request(
            "GET",
            "/agents",
            params={"limit": limit, "offset": offset},
        )

    def get(self, agent_id: str) -> dict:
        """Get an agent by ID."""
        return self._client._request("GET", f"/agents/{agent_id}")

    def create(
        self,
        name: str,
        model: str = "claude-3-sonnet",
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> dict:
        """Create a new agent."""
        data = {
            "name": name,
            "model": model,
            "system_prompt": system_prompt,
            "tools": tools or [],
            **kwargs,
        }
        return self._client._request("POST", "/agents", json=data)

    def update(self, agent_id: str, **kwargs) -> dict:
        """Update an agent."""
        return self._client._request("PATCH", f"/agents/{agent_id}", json=kwargs)

    def delete(self, agent_id: str) -> None:
        """Delete an agent."""
        self._client._request("DELETE", f"/agents/{agent_id}")

    def run(
        self,
        agent_id: str,
        message: str,
        context: Optional[dict] = None,
    ) -> dict:
        """Run an agent with a message."""
        data = {"message": message}
        if context:
            data["context"] = context
        return self._client._request("POST", f"/agents/{agent_id}/run", json=data)


class WorkflowsAPI:
    """API for managing workflows."""

    def __init__(self, client: Client):
        self._client = client

    def list(self, limit: int = 20, offset: int = 0) -> dict:
        """List all workflows."""
        return self._client._request(
            "GET",
            "/workflows",
            params={"limit": limit, "offset": offset},
        )

    def get(self, workflow_id: str) -> dict:
        """Get a workflow by ID."""
        return self._client._request("GET", f"/workflows/{workflow_id}")

    def trigger(self, workflow_id: str, inputs: Optional[dict] = None) -> dict:
        """Trigger a workflow."""
        return self._client._request(
            "POST",
            f"/workflows/{workflow_id}/trigger",
            json={"inputs": inputs or {}},
        )


class ExecutionsAPI:
    """API for managing executions."""

    def __init__(self, client: Client):
        self._client = client

    def get(self, execution_id: str) -> dict:
        """Get an execution by ID."""
        return self._client._request("GET", f"/executions/{execution_id}")

    def list(self, limit: int = 20, offset: int = 0) -> dict:
        """List all executions."""
        return self._client._request(
            "GET",
            "/executions",
            params={"limit": limit, "offset": offset},
        )
