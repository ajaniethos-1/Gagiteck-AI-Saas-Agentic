"""Agent class for local agent creation and execution."""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field

from gagiteck.tool import Tool


@dataclass
class Agent:
    """Create and run AI agents locally.

    Args:
        name: Name of the agent
        model: LLM model to use (default: claude-3-sonnet)
        system_prompt: System prompt for the agent
        tools: List of tools the agent can use
        memory_enabled: Enable conversation memory
        max_tokens: Maximum tokens in response

    Example:
        >>> from gagiteck import Agent, tool
        >>>
        >>> @tool
        >>> def search(query: str) -> str:
        ...     '''Search the web.'''
        ...     return f"Results for: {query}"
        >>>
        >>> agent = Agent(
        ...     name="Research Assistant",
        ...     model="claude-3-opus",
        ...     tools=[search],
        ... )
        >>> response = agent.run("Find info about AI agents")
    """

    name: str
    model: str = "claude-3-sonnet"
    system_prompt: Optional[str] = None
    tools: list[Tool | Callable] = field(default_factory=list)
    memory_enabled: bool = False
    max_tokens: int = 4096
    temperature: float = 0.7

    _conversation_history: list[dict] = field(default_factory=list, repr=False)
    _client: Any = field(default=None, repr=False)

    def __post_init__(self):
        # Convert callable tools to Tool objects
        processed_tools = []
        for t in self.tools:
            if callable(t) and not isinstance(t, Tool):
                processed_tools.append(Tool.from_function(t))
            else:
                processed_tools.append(t)
        self.tools = processed_tools

    def run(self, message: str, context: Optional[dict] = None) -> "AgentResponse":
        """Run the agent with a message.

        Args:
            message: The user message to process
            context: Optional context dictionary

        Returns:
            AgentResponse with the result
        """
        # Add to conversation history
        self._conversation_history.append({"role": "user", "content": message})

        # Build the request
        request = {
            "model": self.model,
            "messages": self._conversation_history if self.memory_enabled else [
                {"role": "user", "content": message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        if self.system_prompt:
            request["system"] = self.system_prompt

        if self.tools:
            request["tools"] = [t.to_dict() for t in self.tools]

        # For now, return a placeholder response
        # In production, this would call the API or local model
        response = AgentResponse(
            content=f"[Agent '{self.name}' would process: {message}]",
            model=self.model,
            tool_calls=[],
        )

        if self.memory_enabled:
            self._conversation_history.append({
                "role": "assistant",
                "content": response.content,
            })

        return response

    def clear_memory(self) -> None:
        """Clear conversation history."""
        self._conversation_history = []


@dataclass
class AgentResponse:
    """Response from an agent run."""

    content: str
    model: str
    tool_calls: list[dict] = field(default_factory=list)
    usage: Optional[dict] = None

    @property
    def text(self) -> str:
        """Get the text content of the response."""
        return self.content
