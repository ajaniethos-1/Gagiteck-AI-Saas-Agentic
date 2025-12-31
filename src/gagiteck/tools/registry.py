"""Tool registry for managing available tools."""

from typing import Dict, List, Optional
from gagiteck.tools.base import Tool


class ToolRegistry:
    """Registry for managing tools.

    Provides a central place to register, discover, and
    retrieve tools.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(my_tool)
        >>> tool = registry.get("my_tool")
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_names(self) -> List[str]:
        """List all tool names."""
        return list(self._tools.keys())

    def to_list(self) -> List[dict]:
        """Get all tools as API format."""
        return [tool.to_dict() for tool in self._tools.values()]

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools


# Global registry instance
default_registry = ToolRegistry()
