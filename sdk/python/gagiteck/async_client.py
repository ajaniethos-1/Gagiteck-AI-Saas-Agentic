"""Gagiteck Async API Client."""

from typing import Optional
import httpx

from gagiteck.exceptions import AuthenticationError, APIError


class AsyncClient:
    """Async client for interacting with the Gagiteck API.

    Args:
        api_key: Your Gagiteck API key (starts with 'ggt_')
        base_url: API base URL (default: https://api.gagiteck.com/v1)
        timeout: Request timeout in seconds (default: 30)
        debug: Enable debug logging (default: False)

    Example:
        >>> import asyncio
        >>> from gagiteck import AsyncClient
        >>>
        >>> async def main():
        ...     async with AsyncClient(api_key="ggt_your_key") as client:
        ...         agents = await client.agents.list()
        ...         print(agents)
        >>>
        >>> asyncio.run(main())
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

        self._http_client: Optional[httpx.AsyncClient] = None

        # Initialize API resources
        self.agents = AsyncAgentsAPI(self)
        self.workflows = AsyncWorkflowsAPI(self)
        self.executions = AsyncExecutionsAPI(self)

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "gagiteck-python/0.1.0",
                },
                timeout=self.timeout,
            )
        return self._http_client

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make an async HTTP request to the API."""
        client = self._get_client()
        try:
            response = await client.request(
                method=method,
                url=path,
                json=json,
                params=params,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {}
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

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


class AsyncAgentsAPI:
    """Async API for managing agents."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def list(self, limit: int = 20, offset: int = 0) -> dict:
        """List all agents."""
        return await self._client._request(
            "GET",
            "/agents",
            params={"limit": limit, "offset": offset},
        )

    async def get(self, agent_id: str) -> dict:
        """Get an agent by ID."""
        return await self._client._request("GET", f"/agents/{agent_id}")

    async def create(
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
        return await self._client._request("POST", "/agents", json=data)

    async def update(self, agent_id: str, **kwargs) -> dict:
        """Update an agent."""
        return await self._client._request("PATCH", f"/agents/{agent_id}", json=kwargs)

    async def delete(self, agent_id: str) -> None:
        """Delete an agent."""
        await self._client._request("DELETE", f"/agents/{agent_id}")

    async def run(
        self,
        agent_id: str,
        message: str,
        context: Optional[dict] = None,
        stream: bool = False,
    ) -> dict:
        """Run an agent with a message.

        Args:
            agent_id: The agent ID
            message: The message to send
            context: Optional context dict
            stream: Whether to stream the response (not yet implemented)
        """
        data = {"message": message, "stream": stream}
        if context:
            data["context"] = context
        return await self._client._request("POST", f"/agents/{agent_id}/run", json=data)


class AsyncWorkflowsAPI:
    """Async API for managing workflows."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def list(self, limit: int = 20, offset: int = 0) -> dict:
        """List all workflows."""
        return await self._client._request(
            "GET",
            "/workflows",
            params={"limit": limit, "offset": offset},
        )

    async def get(self, workflow_id: str) -> dict:
        """Get a workflow by ID."""
        return await self._client._request("GET", f"/workflows/{workflow_id}")

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        steps: Optional[list] = None,
        **kwargs,
    ) -> dict:
        """Create a new workflow."""
        data = {
            "name": name,
            "description": description,
            "steps": steps or [],
            **kwargs,
        }
        return await self._client._request("POST", "/workflows", json=data)

    async def update(self, workflow_id: str, **kwargs) -> dict:
        """Update a workflow."""
        return await self._client._request("PATCH", f"/workflows/{workflow_id}", json=kwargs)

    async def delete(self, workflow_id: str) -> None:
        """Delete a workflow."""
        await self._client._request("DELETE", f"/workflows/{workflow_id}")

    async def trigger(self, workflow_id: str, inputs: Optional[dict] = None) -> dict:
        """Trigger a workflow."""
        return await self._client._request(
            "POST",
            f"/workflows/{workflow_id}/trigger",
            json={"inputs": inputs or {}},
        )


class AsyncExecutionsAPI:
    """Async API for managing executions."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def get(self, execution_id: str) -> dict:
        """Get an execution by ID."""
        return await self._client._request("GET", f"/executions/{execution_id}")

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> dict:
        """List all executions."""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        return await self._client._request("GET", "/executions", params=params)

    async def cancel(self, execution_id: str) -> dict:
        """Cancel a running execution."""
        return await self._client._request("POST", f"/executions/{execution_id}/cancel")

    async def wait(
        self,
        execution_id: str,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> dict:
        """Wait for an execution to complete.

        Args:
            execution_id: The execution ID
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait (None for no timeout)
        """
        import asyncio
        import time

        start_time = time.time()
        while True:
            execution = await self.get(execution_id)
            if execution["status"] in ("completed", "failed", "cancelled"):
                return execution

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Execution {execution_id} did not complete within {timeout}s")

            await asyncio.sleep(poll_interval)
