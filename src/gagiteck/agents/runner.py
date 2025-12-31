"""Agent execution runner."""

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional
from datetime import datetime
import asyncio

from gagiteck.agents.base import Agent, AgentStatus
from gagiteck.agents.memory import ConversationMemory


@dataclass
class ToolCall:
    """Record of a tool call."""
    id: str
    tool_name: str
    input: dict
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0


@dataclass
class AgentResponse:
    """Response from an agent run."""
    content: str
    agent_id: str
    model: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def text(self) -> str:
        """Get text content."""
        return self.content


class AgentRunner:
    """Executes agents and manages their lifecycle.

    The runner handles:
    - Message processing
    - Tool execution
    - Memory management
    - Streaming responses

    Example:
        >>> runner = AgentRunner()
        >>> agent = Agent(name="Assistant")
        >>> response = await runner.run(agent, "Hello!")
        >>> print(response.text)
    """

    def __init__(
        self,
        llm_client: Any = None,
        default_model: str = "claude-3-sonnet",
    ):
        self.llm_client = llm_client
        self.default_model = default_model
        self._running_agents: dict[str, Agent] = {}

    async def run(
        self,
        agent: Agent,
        message: str,
        context: Optional[dict] = None,
        memory: Optional[ConversationMemory] = None,
    ) -> AgentResponse:
        """Run an agent with a message.

        Args:
            agent: The agent to run
            message: User message
            context: Optional context
            memory: Optional conversation memory

        Returns:
            AgentResponse with the result
        """
        agent.status = AgentStatus.RUNNING
        self._running_agents[agent.id] = agent

        try:
            # Build messages
            messages = []
            if memory:
                messages.extend(memory.get_messages())
            messages.append({"role": "user", "content": message})

            # Add to memory
            if memory:
                memory.add_message("user", message)

            # Execute agent logic
            response = await self._execute(agent, messages, context)

            # Add response to memory
            if memory:
                memory.add_message("assistant", response.content)

            agent.status = AgentStatus.COMPLETED
            return response

        except Exception as e:
            agent.status = AgentStatus.FAILED
            raise

        finally:
            self._running_agents.pop(agent.id, None)

    async def run_stream(
        self,
        agent: Agent,
        message: str,
        context: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """Run agent with streaming response.

        Yields:
            Chunks of the response text
        """
        agent.status = AgentStatus.RUNNING

        try:
            # Placeholder for streaming implementation
            response = await self.run(agent, message, context)
            for word in response.content.split():
                yield word + " "
                await asyncio.sleep(0.05)

        finally:
            agent.status = AgentStatus.COMPLETED

    async def _execute(
        self,
        agent: Agent,
        messages: list[dict],
        context: Optional[dict],
    ) -> AgentResponse:
        """Execute the agent logic."""
        # Build request for LLM
        request = {
            "model": agent.config.model,
            "messages": messages,
            "max_tokens": agent.config.max_tokens,
            "temperature": agent.config.temperature,
        }

        if agent.system_prompt:
            request["system"] = agent.system_prompt

        if agent.tools:
            request["tools"] = [
                t.to_dict() if hasattr(t, "to_dict") else t
                for t in agent.tools
            ]

        # For now, return a placeholder
        # In production, this calls the actual LLM API
        content = f"[Agent '{agent.name}' processed message]"

        return AgentResponse(
            content=content,
            agent_id=agent.id,
            model=agent.config.model,
        )

    async def _execute_tool(
        self,
        agent: Agent,
        tool_name: str,
        tool_input: dict,
    ) -> ToolCall:
        """Execute a tool call."""
        import time
        import uuid

        start = time.time()
        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            tool_name=tool_name,
            input=tool_input,
        )

        # Find the tool
        tool = next((t for t in agent.tools if t.name == tool_name), None)
        if not tool:
            tool_call.error = f"Tool '{tool_name}' not found"
            return tool_call

        try:
            result = tool(**tool_input)
            if asyncio.iscoroutine(result):
                result = await result
            tool_call.output = result
        except Exception as e:
            tool_call.error = str(e)

        tool_call.duration_ms = int((time.time() - start) * 1000)
        return tool_call

    def cancel(self, agent_id: str) -> bool:
        """Cancel a running agent."""
        if agent_id in self._running_agents:
            self._running_agents[agent_id].status = AgentStatus.IDLE
            return True
        return False
