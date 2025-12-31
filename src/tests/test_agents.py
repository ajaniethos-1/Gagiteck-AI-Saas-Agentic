"""Tests for core agent framework."""

import pytest
from gagiteck.agents.base import Agent, AgentConfig, AgentStatus
from gagiteck.agents.memory import ConversationMemory, SummarizingMemory


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_default_config(self):
        """Config should have sensible defaults."""
        config = AgentConfig()
        assert config.model == "claude-3-sonnet"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.max_iterations == 25
        assert config.timeout_ms == 120000

    def test_custom_config(self):
        """Config should accept custom values."""
        config = AgentConfig(
            model="claude-3-opus",
            max_tokens=8192,
            temperature=0.5,
        )
        assert config.model == "claude-3-opus"
        assert config.max_tokens == 8192
        assert config.temperature == 0.5


class TestAgent:
    """Tests for Agent class."""

    def test_agent_auto_generates_id(self):
        """Agent should auto-generate ID if not provided."""
        agent = Agent(name="Test")
        assert agent.id is not None
        assert agent.id.startswith("agent_")

    def test_agent_uses_provided_id(self):
        """Agent should use provided ID."""
        agent = Agent(id="custom_id", name="Test")
        assert agent.id == "custom_id"

    def test_agent_default_status(self):
        """Agent should start in IDLE status."""
        agent = Agent(name="Test")
        assert agent.status == AgentStatus.IDLE

    def test_agent_add_tool(self):
        """Agent should allow adding tools."""
        agent = Agent(name="Test")
        mock_tool = type("Tool", (), {"name": "test_tool"})()

        agent.add_tool(mock_tool)
        assert len(agent.tools) == 1

    def test_agent_remove_tool(self):
        """Agent should allow removing tools."""
        mock_tool = type("Tool", (), {"name": "test_tool"})()
        agent = Agent(name="Test", tools=[mock_tool])

        agent.remove_tool("test_tool")
        assert len(agent.tools) == 0

    def test_agent_to_dict(self):
        """Agent should serialize to dictionary."""
        agent = Agent(
            id="agent_123",
            name="Test Agent",
            system_prompt="Be helpful",
        )

        d = agent.to_dict()
        assert d["id"] == "agent_123"
        assert d["name"] == "Test Agent"
        assert d["system_prompt"] == "Be helpful"
        assert d["status"] == "idle"

    def test_agent_from_dict(self):
        """Agent should deserialize from dictionary."""
        data = {
            "id": "agent_123",
            "name": "Test Agent",
            "system_prompt": "Be helpful",
            "config": {"model": "claude-3-opus"},
        }

        agent = Agent.from_dict(data)
        assert agent.id == "agent_123"
        assert agent.name == "Test Agent"
        assert agent.config.model == "claude-3-opus"


class TestConversationMemory:
    """Tests for ConversationMemory."""

    def test_add_message(self):
        """Memory should store messages."""
        memory = ConversationMemory()
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")

        assert memory.message_count == 2

    def test_get_messages(self):
        """Memory should return messages as dicts."""
        memory = ConversationMemory()
        memory.add_message("user", "Hello")

        messages = memory.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_max_messages_limit(self):
        """Memory should respect max_messages limit."""
        memory = ConversationMemory(max_messages=3)

        for i in range(5):
            memory.add_message("user", f"Message {i}")

        assert memory.message_count == 3
        messages = memory.get_messages()
        assert messages[0]["content"] == "Message 2"

    def test_clear_memory(self):
        """Memory should clear all messages."""
        memory = ConversationMemory()
        memory.add_message("user", "Hello")
        memory.clear()

        assert memory.message_count == 0

    def test_get_messages_with_limit(self):
        """Memory should return limited messages."""
        memory = ConversationMemory()
        for i in range(5):
            memory.add_message("user", f"Message {i}")

        messages = memory.get_messages(limit=2)
        assert len(messages) == 2
        assert messages[0]["content"] == "Message 3"

    def test_context_window(self):
        """Memory should return messages within token limit."""
        memory = ConversationMemory()
        memory.add_message("user", "Short")
        memory.add_message("user", "A" * 1000)  # ~250 tokens

        messages = memory.get_context_window(max_tokens=100)
        assert len(messages) == 1
        assert messages[0]["content"] == "Short"


class TestSummarizingMemory:
    """Tests for SummarizingMemory."""

    def test_recent_messages_kept(self):
        """Memory should keep recent messages."""
        memory = SummarizingMemory(recent_count=3)

        for i in range(3):
            memory.add_message("user", f"Message {i}")

        messages = memory.get_messages()
        assert len(messages) == 3

    def test_clear_memory(self):
        """Memory should clear all content."""
        memory = SummarizingMemory()
        memory.add_message("user", "Hello")
        memory.clear()

        messages = memory.get_messages()
        assert len(messages) == 0
