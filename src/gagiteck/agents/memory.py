"""Memory management for agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """A conversation message."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class Memory(ABC):
    """Abstract base class for agent memory."""

    @abstractmethod
    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory."""
        pass

    @abstractmethod
    def get_messages(self, limit: Optional[int] = None) -> list[dict]:
        """Get messages from memory."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory."""
        pass


class ConversationMemory(Memory):
    """Simple conversation memory.

    Stores messages in a sliding window.

    Args:
        max_messages: Maximum messages to retain
        max_tokens: Maximum tokens to retain (approximate)

    Example:
        >>> memory = ConversationMemory(max_messages=20)
        >>> memory.add_message("user", "Hello!")
        >>> memory.add_message("assistant", "Hi there!")
        >>> print(memory.get_messages())
    """

    def __init__(
        self,
        max_messages: int = 50,
        max_tokens: Optional[int] = None,
    ):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._messages: list[Message] = []

    def add_message(self, role: str, content: str, **metadata) -> None:
        """Add a message to memory."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata,
        )
        self._messages.append(message)

        # Trim if over limit
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_messages(self, limit: Optional[int] = None) -> list[dict]:
        """Get messages as list of dicts."""
        messages = self._messages
        if limit:
            messages = messages[-limit:]

        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

    def clear(self) -> None:
        """Clear all messages."""
        self._messages = []

    def get_context_window(self, max_tokens: int) -> list[dict]:
        """Get messages that fit within token limit.

        Uses approximate token counting (4 chars = 1 token).
        """
        messages = []
        total_tokens = 0

        for message in reversed(self._messages):
            # Approximate token count
            tokens = len(message.content) // 4

            if total_tokens + tokens > max_tokens:
                break

            messages.insert(0, {
                "role": message.role,
                "content": message.content,
            })
            total_tokens += tokens

        return messages

    @property
    def message_count(self) -> int:
        """Get number of messages."""
        return len(self._messages)


class SummarizingMemory(Memory):
    """Memory that summarizes old conversations.

    Keeps recent messages and summarizes older ones.
    """

    def __init__(
        self,
        recent_count: int = 10,
        summarizer: Optional[callable] = None,
    ):
        self.recent_count = recent_count
        self.summarizer = summarizer
        self._messages: list[Message] = []
        self._summary: Optional[str] = None

    def add_message(self, role: str, content: str, **metadata) -> None:
        """Add a message."""
        self._messages.append(Message(
            role=role,
            content=content,
            metadata=metadata,
        ))

        # Summarize if needed
        if len(self._messages) > self.recent_count * 2:
            self._summarize()

    def _summarize(self) -> None:
        """Summarize older messages."""
        if not self.summarizer:
            # Simple truncation without summarization
            self._messages = self._messages[-self.recent_count:]
            return

        # Get messages to summarize
        to_summarize = self._messages[:-self.recent_count]

        # Create summary
        text = "\n".join(f"{m.role}: {m.content}" for m in to_summarize)
        self._summary = self.summarizer(text)

        # Keep only recent messages
        self._messages = self._messages[-self.recent_count:]

    def get_messages(self, limit: Optional[int] = None) -> list[dict]:
        """Get messages with summary."""
        messages = []

        # Add summary as system message
        if self._summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {self._summary}",
            })

        # Add recent messages
        recent = self._messages[-limit:] if limit else self._messages
        messages.extend([
            {"role": m.role, "content": m.content}
            for m in recent
        ])

        return messages

    def clear(self) -> None:
        """Clear all memory."""
        self._messages = []
        self._summary = None
