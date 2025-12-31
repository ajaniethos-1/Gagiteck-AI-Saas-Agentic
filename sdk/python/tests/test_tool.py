"""Tests for the Tool class and decorator."""

import pytest
from gagiteck import Tool, tool


class TestTool:
    """Tests for the Tool class."""

    def test_tool_creation(self):
        """Tool should be created with required fields."""
        t = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
        )
        assert t.name == "test_tool"
        assert t.description == "A test tool"

    def test_tool_with_function(self):
        """Tool should execute its function."""
        def add(a: int, b: int) -> int:
            return a + b

        t = Tool(
            name="add",
            description="Add two numbers",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
            function=add,
        )

        result = t(a=2, b=3)
        assert result == 5

    def test_tool_without_function_raises(self):
        """Tool without function should raise on call."""
        t = Tool(name="empty", description="Empty tool")
        with pytest.raises(ValueError, match="has no function"):
            t()

    def test_tool_to_dict(self):
        """Tool should convert to API format."""
        t = Tool(
            name="search",
            description="Search the web",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
            },
        )

        d = t.to_dict()
        assert d["type"] == "function"
        assert d["function"]["name"] == "search"
        assert d["function"]["description"] == "Search the web"

    def test_tool_from_function(self):
        """Tool should be created from a function."""
        def greet(name: str) -> str:
            """Greet someone by name."""
            return f"Hello, {name}!"

        t = Tool.from_function(greet)
        assert t.name == "greet"
        assert "Greet someone" in t.description
        assert t.parameters["properties"]["name"]["type"] == "string"
        assert "name" in t.parameters["required"]

    def test_tool_from_function_optional_params(self):
        """Tool should handle optional parameters."""
        def greet(name: str, greeting: str = "Hello") -> str:
            """Greet someone."""
            return f"{greeting}, {name}!"

        t = Tool.from_function(greet)
        assert "name" in t.parameters["required"]
        assert "greeting" not in t.parameters.get("required", [])


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_tool_decorator(self):
        """@tool decorator should create a Tool."""
        @tool
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        assert isinstance(multiply, Tool)
        assert multiply.name == "multiply"
        assert "Multiply" in multiply.description

    def test_tool_decorator_execution(self):
        """Decorated tool should execute."""
        @tool
        def double(n: int) -> int:
            """Double a number."""
            return n * 2

        result = double(n=5)
        assert result == 10

    def test_tool_decorator_preserves_docstring(self):
        """Decorator should preserve function docstring."""
        @tool
        def example():
            """This is the docstring."""
            pass

        assert example.description == "This is the docstring."

    def test_tool_decorator_type_inference(self):
        """Decorator should infer types from hints."""
        @tool
        def process(
            text: str,
            count: int,
            ratio: float,
            flag: bool,
        ) -> dict:
            """Process data."""
            return {}

        props = process.parameters["properties"]
        assert props["text"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["ratio"]["type"] == "number"
        assert props["flag"]["type"] == "boolean"
