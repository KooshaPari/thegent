"""Execution registries and history.

Domain: Registry & History
Classes:
- RunRegistry: Run management
- ChatHistory: Chat history
- MessageRegistry: Message registry
- AuditRegistry: Audit records
- CheckpointRegistry: Checkpoint management
- ChatEntry, MessageEntry, AuditEntry: Data models
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RunRegistry:
    """Registry for execution runs."""

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}

    def register(self, run_id: str, data: dict[str, Any]) -> None:
        """Register a new run."""
        data["registered_at"] = datetime.now().isoformat()
        self._runs[run_id] = data

    def get(self, run_id: str) -> dict[str, Any] | None:
        """Get run data."""
        return self._runs.get(run_id)

    def update(self, run_id: str, data: dict[str, Any]) -> None:
        """Update run data."""
        if run_id in self._runs:
            self._runs[run_id].update(data)
            self._runs[run_id]["updated_at"] = datetime.now().isoformat()

    def list_all(self) -> list[dict[str, Any]]:
        """List all runs."""
        return list(self._runs.values())


class ChatEntry(BaseModel):
    """Chat entry model."""
    entry_id: str
    role: str
    content: str
    timestamp: str
    metadata: dict = Field(default_factory=dict)


class ChatHistory:
    """Manages chat history."""

    def __init__(self) -> None:
        self._history: list[ChatEntry] = []

    def add(self, entry: ChatEntry) -> None:
        """Add chat entry."""
        self._history.append(entry)

    def get_all(self) -> list[ChatEntry]:
        """Get all entries."""
        return self._history.copy()

    def clear(self) -> None:
        """Clear history."""
        self._history.clear()


class MessageEntry(BaseModel):
    """Message entry model."""
    message_id: str
    channel: str
    content: str
    sender: str
    timestamp: str
    metadata: dict = Field(default_factory=dict)


class MessageRegistry:
    """Registry for messages."""

    def __init__(self) -> None:
        self._messages: dict[str, MessageEntry] = {}

    def register(self, message: MessageEntry) -> None:
        """Register a message."""
        self._messages[message.message_id] = message

    def get(self, message_id: str) -> MessageEntry | None:
        """Get message by ID."""
        return self._messages.get(message_id)

    def list_by_channel(self, channel: str) -> list[MessageEntry]:
        """List messages by channel."""
        return [m for m in self._messages.values() if m.channel == channel]


class AuditEntry(BaseModel):
    """Audit entry model."""
    entry_id: str
    action: str
    actor: str
    target: str
    timestamp: str
    result: str
    metadata: dict = Field(default_factory=dict)


class AuditRegistry:
    """Registry for audit entries."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def log(self, entry: AuditEntry) -> None:
        """Log audit entry."""
        self._entries.append(entry)

    def query(self, actor: str | None = None, action: str | None = None) -> list[AuditEntry]:
        """Query audit entries."""
        results = self._entries
        if actor:
            results = [e for e in results if e.actor == actor]
        if action:
            results = [e for e in results if e.action == action]
        return results


class CheckpointRegistry:
    """Registry for execution checkpoints."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, list[dict[str, Any]]] = {}

    def save(self, run_id: str, checkpoint: dict[str, Any]) -> None:
        """Save checkpoint."""
        if run_id not in self._checkpoints:
            self._checkpoints[run_id] = []
        checkpoint["saved_at"] = datetime.now().isoformat()
        self._checkpoints[run_id].append(checkpoint)

    def get_latest(self, run_id: str) -> dict[str, Any] | None:
        """Get latest checkpoint."""
        checkpoints = self._checkpoints.get(run_id, [])
        return checkpoints[-1] if checkpoints else None

    def get_all(self, run_id: str) -> list[dict[str, Any]]:
        """Get all checkpoints for run."""
        return self._checkpoints.get(run_id, [])


__all__ = [
    "AuditEntry",
    "AuditRegistry",
    "ChatEntry",
    "ChatHistory",
    "CheckpointRegistry",
    "MessageEntry",
    "MessageRegistry",
    "RunRegistry",
]
