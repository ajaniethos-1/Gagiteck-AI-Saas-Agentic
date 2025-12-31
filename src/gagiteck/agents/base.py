"""Base Agent class and configuration."""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class AgentStatus(Enum):
    """Agent status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentConfig:
    """Configuration for an agent.

    Attributes:
        model: The LLM model to use
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        max_iterations: Maximum reasoning iterations
        timeout_ms: Execution timeout in milliseconds
    """
    model: str = "claude-3-sonnet"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_iterations: int = 25
    timeout_ms: int = 120000
    streaming: bool = False


@dataclass
class Agent:
    """An autonomous AI agent.

    Agents can reason, plan, and execute tasks using tools.

    Attributes:
        id: Unique agent identifier
        name: Human-readable name
        system_prompt: System instructions for the agent
        config: Agent configuration
        tools: List of tools the agent can use
        metadata: Additional metadata

    Example:
        >>> agent = Agent(
        ...     name="Research Assistant",
        ...     system_prompt="You are a helpful research assistant.",
        ...     config=AgentConfig(model="claude-3-opus"),
        ... )
    """
    id: Optional[str] = None
    name: str = "Agent"
    system_prompt: Optional[str] = None
    config: AgentConfig = field(default_factory=AgentConfig)
    tools: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE

    def __post_init__(self):
        if self.id is None:
            import uuid
            self.id = f"agent_{uuid.uuid4().hex[:12]}"

    def add_tool(self, tool: Any) -> "Agent":
        """Add a tool to the agent."""
        self.tools.append(tool)
        return self

    def remove_tool(self, tool_name: str) -> "Agent":
        """Remove a tool by name."""
        self.tools = [t for t in self.tools if t.name != tool_name]
        return self

    def to_dict(self) -> dict:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "system_prompt": self.system_prompt,
            "config": {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "max_iterations": self.config.max_iterations,
                "timeout_ms": self.config.timeout_ms,
            },
            "tools": [t.to_dict() if hasattr(t, "to_dict") else str(t) for t in self.tools],
            "metadata": self.metadata,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """Create agent from dictionary."""
        config_data = data.get("config", {})
        config = AgentConfig(
            model=config_data.get("model", "claude-3-sonnet"),
            max_tokens=config_data.get("max_tokens", 4096),
            temperature=config_data.get("temperature", 0.7),
            max_iterations=config_data.get("max_iterations", 25),
            timeout_ms=config_data.get("timeout_ms", 120000),
        )
        return cls(
            id=data.get("id"),
            name=data.get("name", "Agent"),
            system_prompt=data.get("system_prompt"),
            config=config,
            metadata=data.get("metadata", {}),
        )
