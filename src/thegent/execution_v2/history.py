"""Chat history module.

Extracted from execution.py.
"""

from pathlib import Path
from pydantic import BaseModel


class ChatEntry(BaseModel):
    """Chat entry model."""
    role: str
    content: str


class ChatHistory:
    """Manages chat history."""

    def __init__(self, chat_path: Path) -> None:
        self.chat_path = chat_path

    def append(self, entry: ChatEntry) -> None:
        """Append entry."""

    def load(self, limit: int | None = None):
        """Load entries."""
        return []


class MessageEntry(BaseModel):
    """Message entry model."""
    msg_id: str
    status: str


class MessageRegistry:
    """Manages message registry."""

    def __init__(self, messages_path: Path) -> None:
        self.messages_path = messages_path

    def push(self, entry: MessageEntry) -> None:
        """Push entry."""

    def list_pending(self):
        """List pending."""
        return []


__all__ = ["ChatEntry", "ChatHistory", "MessageEntry", "MessageRegistry"]
