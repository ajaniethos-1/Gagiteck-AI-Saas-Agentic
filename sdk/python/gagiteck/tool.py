"""Tool definitions for agents."""

from typing import Any, Callable, Optional, get_type_hints
from dataclasses import dataclass, field
import inspect


@dataclass
class Tool:
    """A tool that agents can use.

    Args:
        name: Name of the tool
        description: Description of what the tool does
        parameters: JSON schema for tool parameters
        function: The function to execute

    Example:
        >>> tool = Tool(
        ...     name="calculator",
        ...     description="Perform math calculations",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "expression": {"type": "string", "description": "Math expression"}
        ...         },
        ...         "required": ["expression"]
        ...     },
        ...     function=lambda expr: eval(expr)
        ... )
    """

    name: str
    description: str
    parameters: dict = field(default_factory=dict)
    function: Optional[Callable] = None

    def __call__(self, **kwargs) -> Any:
        """Execute the tool."""
        if self.function is None:
            raise ValueError(f"Tool '{self.name}' has no function defined")
        return self.function(**kwargs)

    def to_dict(self) -> dict:
        """Convert to API-compatible dictionary."""
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
        """Create a Tool from a function.

        The function's docstring becomes the description.
        Type hints are used to generate the parameter schema.
        """
        name = func.__name__
        description = func.__doc__ or f"Execute {name}"

        # Get type hints and generate schema
        hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}
        sig = inspect.signature(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = hints.get(param_name, str)
            json_type = _python_type_to_json(param_type)

            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter: {param_name}",
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
            description=description.strip(),
            parameters=parameters,
            function=func,
        )


def tool(func: Callable) -> Tool:
    """Decorator to create a Tool from a function.

    Example:
        >>> @tool
        >>> def search_web(query: str) -> str:
        ...     '''Search the web for information.'''
        ...     return requests.get(f"https://api.search.com?q={query}").text
        >>>
        >>> agent = Agent(tools=[search_web])
    """
    return Tool.from_function(func)


def _python_type_to_json(python_type: type) -> str:
    """Convert Python type to JSON schema type."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return type_map.get(python_type, "string")
