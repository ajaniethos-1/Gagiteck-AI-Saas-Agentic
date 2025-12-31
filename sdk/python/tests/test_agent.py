"""Tests for the Agent class."""

import pytest
from gagiteck import Agent
from gagiteck.agent import AgentResponse


class TestAgent:
    """Tests for the Agent class."""

    def test_agent_creation_defaults(self):
        """Agent should have sensible defaults."""
        agent = Agent(name="Test Agent")
        assert agent.name == "Test Agent"
        assert agent.model == "claude-3-sonnet"
        assert agent.system_prompt is None
        assert agent.tools == []
        assert agent.memory_enabled is False

    def test_agent_creation_custom(self):
        """Agent should accept custom configuration."""
        agent = Agent(
            name="Custom Agent",
            model="claude-3-opus",
            system_prompt="You are helpful.",
            memory_enabled=True,
            max_tokens=2048,
            temperature=0.5,
        )
        assert agent.name == "Custom Agent"
        assert agent.model == "claude-3-opus"
        assert agent.system_prompt == "You are helpful."
        assert agent.memory_enabled is True
        assert agent.max_tokens == 2048
        assert agent.temperature == 0.5

    def test_agent_run_returns_response(self):
        """Agent run should return AgentResponse."""
        agent = Agent(name="Test Agent")
        response = agent.run("Hello")
        assert isinstance(response, AgentResponse)
        assert response.model == "claude-3-sonnet"

    def test_agent_run_with_memory(self):
        """Agent should maintain conversation history with memory enabled."""
        agent = Agent(name="Memory Agent", memory_enabled=True)

        agent.run("First message")
        agent.run("Second message")

        assert len(agent._conversation_history) == 4  # 2 user + 2 assistant

    def test_agent_run_without_memory(self):
        """Agent should not maintain history without memory."""
        agent = Agent(name="No Memory Agent", memory_enabled=False)

        agent.run("First message")
        agent.run("Second message")

        # History still tracks for internal use but not sent to API
        assert len(agent._conversation_history) == 2  # Only user messages

    def test_agent_clear_memory(self):
        """Agent should clear memory when requested."""
        agent = Agent(name="Memory Agent", memory_enabled=True)

        agent.run("Message 1")
        agent.run("Message 2")
        agent.clear_memory()

        assert len(agent._conversation_history) == 0


class TestAgentResponse:
    """Tests for AgentResponse."""

    def test_response_text_property(self):
        """Response should have text property."""
        response = AgentResponse(
            content="Hello, world!",
            model="claude-3-sonnet",
        )
        assert response.text == "Hello, world!"

    def test_response_with_tool_calls(self):
        """Response should handle tool calls."""
        response = AgentResponse(
            content="Result",
            model="claude-3-sonnet",
            tool_calls=[{"name": "search", "input": {"q": "test"}}],
        )
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["name"] == "search"

    def test_response_with_usage(self):
        """Response should track token usage."""
        response = AgentResponse(
            content="Result",
            model="claude-3-sonnet",
            usage={"input_tokens": 100, "output_tokens": 50},
        )
        assert response.usage["input_tokens"] == 100
        assert response.usage["output_tokens"] == 50
