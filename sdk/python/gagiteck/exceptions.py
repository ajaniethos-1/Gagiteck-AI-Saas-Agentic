"""Exception classes for Gagiteck SDK."""


class GagiteckError(Exception):
    """Base exception for all Gagiteck errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class APIError(GagiteckError):
    """Error from the Gagiteck API."""

    def __init__(self, code: int, message: str):
        self.code = code
        super().__init__(f"API Error {code}: {message}")


class AuthenticationError(GagiteckError):
    """Authentication failed."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(429, message)


class ValidationError(GagiteckError):
    """Invalid input data."""

    pass


class AgentError(GagiteckError):
    """Error during agent execution."""

    pass


class ToolError(GagiteckError):
    """Error during tool execution."""

    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")
