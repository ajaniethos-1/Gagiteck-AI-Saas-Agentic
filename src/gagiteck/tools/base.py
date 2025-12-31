"""Base Tool class and decorator."""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, get_type_hints
import inspect
import asyncio


@dataclass
class Tool:
    """A tool that agents can use to perform actions.

    Tools extend agent capabilities by providing access to
    external systems, APIs, or custom functions.

    Attributes:
        name: Unique tool name
        description: What the tool does
        parameters: JSON schema for parameters
        function: The callable to execute

    Example:
        >>> @tool
        >>> def search_web(query: str) -> str:
        ...     '''Search the web for information.'''
        ...     return search_api(query)
    """
    name: str
    description: str
    parameters: dict = field(default_factory=dict)
    function: Optional[Callable] = None
    is_async: bool = False

    def __call__(self, **kwargs) -> Any:
        """Execute the tool synchronously."""
        if self.function is None:
            raise ValueError(f"Tool '{self.name}' has no function")

        result = self.function(**kwargs)

        if asyncio.iscoroutine(result):
            return asyncio.get_event_loop().run_until_complete(result)

        return result

    async def call_async(self, **kwargs) -> Any:
        """Execute the tool asynchronously."""
        if self.function is None:
            raise ValueError(f"Tool '{self.name}' has no function")

        result = self.function(**kwargs)

        if asyncio.iscoroutine(result):
            return await result

        return result

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    @classmethod
    def from_function(cls, func: Callable) -> "Tool":
        """Create a Tool from a function."""
        name = func.__name__
        description = inspect.getdoc(func) or f"Execute {name}"
        is_async = asyncio.iscoroutinefunction(func)

        # Build parameter schema from type hints
        hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}
        sig = inspect.signature(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            python_type = hints.get(param_name, str)
            json_type = _type_to_json_schema(python_type)

            properties[param_name] = {
                "type": json_type,
                "description": f"{param_name} parameter",
            }

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        parameters = {
            "type": "object",
            "properties": properties,
        }
        if required:
            parameters["required"] = required

        return cls(
            name=name,
            description=description,
            parameters=parameters,
            function=func,
            is_async=is_async,
        )


def tool(func: Callable) -> Tool:
    """Decorator to create a Tool from a function.

    Example:
        >>> @tool
        >>> def calculate(expression: str) -> float:
        ...     '''Evaluate a math expression.'''
        ...     return eval(expression)
        >>>
        >>> result = calculate(expression="2 + 2")
        >>> print(result)  # 4
    """
    return Tool.from_function(func)


def _type_to_json_schema(python_type: type) -> str:
    """Convert Python type to JSON schema type."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    # Handle Optional types
    origin = getattr(python_type, "__origin__", None)
    if origin is type(None):
        return "null"

    return type_map.get(python_type, "string")
