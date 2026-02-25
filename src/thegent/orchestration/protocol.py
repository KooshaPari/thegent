"""InterAgentProtocol: Typed Message Schema for sub-agent communication.

This module provides Pydantic models for structured inter-agent messaging
with JSONL serialization support.

Models:
- SubAgentRequest: Outgoing request to a sub-agent
- SubAgentResult: Response/result from a sub-agent
- SubAgentEvent: Event notification during sub-agent execution
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, UTC
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class SubAgentStatus(StrEnum):
    """Status values for sub-agent lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SubAgentEventType(StrEnum):
    """Event types emitted during sub-agent execution."""

    STARTED = "started"
    PROGRESS = "progress"
    TOOL_USE = "tool_use"
    MESSAGE = "message"
    ERROR = "error"
    COMPLETED = "completed"
    HEARTBEAT = "heartbeat"
    CANCELLED = "cancelled"


class SubAgentRequest(BaseModel):
    """Request message sent to a sub-agent.

    This is the primary message type for dispatching work to sub-agents.
    Contains all context and parameters needed for execution.
    """

    request_id: str = Field(
        default_factory=lambda: f"req_{int(time.time() * 1000):x}",
        description="Unique identifier for this request",
    )
    parent_id: str | None = Field(
        default=None,
        description="ID of the parent agent that dispatched this request",
    )
    agent_type: str = Field(
        description="Type/name of the sub-agent to invoke",
    )
    task: str = Field(
        description="The task/prompt to execute",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context data for the sub-agent",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Maximum execution time in seconds",
    )
    priority: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Priority level (lower = higher priority)",
    )
    capabilities: list[str] = Field(
        default_factory=list,
        description="Required capabilities for this sub-agent",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO timestamp of request creation",
    )

    def to_jsonl(self) -> str:
        """Serialize to JSONL format."""
        return self.model_dump_json() + "\n"

    @classmethod
    def from_jsonl(cls, line: str) -> SubAgentRequest:
        """Deserialize from JSONL format."""
        return cls.model_validate_json(line)

    def with_updated_context(self, updates: dict[str, Any]) -> SubAgentRequest:
        """Create a copy with updated context."""
        new_context = {**self.context, **updates}
        return self.model_copy(update={"context": new_context})


class SubAgentResult(BaseModel):
    """Result message returned from a sub-agent.

    Contains the outcome of sub-agent execution including success/failure
    status, outputs, and execution metrics.
    """

    request_id: str = Field(
        description="ID of the original request this result is for",
    )
    result_id: str = Field(
        default_factory=lambda: f"res_{int(time.time() * 1000):x}",
        description="Unique identifier for this result",
    )
    parent_id: str | None = Field(
        default=None,
        description="ID of the parent agent that dispatched the request",
    )
    agent_type: str = Field(
        description="Type/name of the sub-agent that produced this result",
    )
    status: SubAgentStatus = Field(
        description="Final execution status",
    )
    output: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured output from the sub-agent",
    )
    error: str | None = Field(
        default=None,
        description="Error message if status is failed",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metrics (duration, tokens, etc.)",
    )
    artifacts: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Files or resources produced by the sub-agent",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO timestamp of result creation",
    )

    @property
    def is_success(self) -> bool:
        """Check if the result represents a successful execution."""
        return self.status == SubAgentStatus.COMPLETED

    @property
    def is_terminal(self) -> bool:
        """Check if the status is a terminal state."""
        return self.status in (
            SubAgentStatus.COMPLETED,
            SubAgentStatus.FAILED,
            SubAgentStatus.CANCELLED,
            SubAgentStatus.TIMEOUT,
        )

    def to_jsonl(self) -> str:
        """Serialize to JSONL format."""
        return self.model_dump_json() + "\n"

    @classmethod
    def from_jsonl(cls, line: str) -> SubAgentResult:
        """Deserialize from JSONL format."""
        return cls.model_validate_json(line)

    def with_error(self, error: str) -> SubAgentResult:
        """Create a copy with an error, marking status as failed."""
        return self.model_copy(
            update={
                "status": SubAgentStatus.FAILED,
                "error": error,
            }
        )


class SubAgentEvent(BaseModel):
    """Event message emitted during sub-agent execution.

    Streams real-time updates about sub-agent progress, tool usage,
    errors, and other lifecycle events.
    """

    event_id: str = Field(
        default_factory=lambda: f"evt_{int(time.time() * 1000):x}",
        description="Unique identifier for this event",
    )
    request_id: str = Field(
        description="ID of the request this event relates to",
    )
    parent_id: str | None = Field(
        default=None,
        description="ID of the parent agent",
    )
    event_type: SubAgentEventType = Field(
        description="Type of event",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
    )
    message: str | None = Field(
        default=None,
        description="Human-readable event message",
    )
    severity: str = Field(
        default="info",
        description="Event severity level",
    )
    sequence: int = Field(
        default=0,
        description="Sequence number for ordering events",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO timestamp of event emission",
    )

    def to_jsonl(self) -> str:
        """Serialize to JSONL format."""
        return self.model_dump_json() + "\n"

    @classmethod
    def from_jsonl(cls, line: str) -> SubAgentEvent:
        """Deserialize from JSONL format."""
        return cls.model_validate_json(line)

    @classmethod
    def create_start(
        cls,
        request_id: str,
        parent_id: str | None = None,
        agent_type: str = "",
    ) -> SubAgentEvent:
        """Factory for STARTED event."""
        return cls(
            request_id=request_id,
            parent_id=parent_id,
            event_type=SubAgentEventType.STARTED,
            payload={"agent_type": agent_type},
            message=f"Sub-agent {agent_type} started execution",
            severity="info",
        )

    @classmethod
    def create_progress(
        cls,
        request_id: str,
        progress: float,
        message: str | None = None,
        parent_id: str | None = None,
    ) -> SubAgentEvent:
        """Factory for PROGRESS event."""
        return cls(
            request_id=request_id,
            parent_id=parent_id,
            event_type=SubAgentEventType.PROGRESS,
            payload={"progress": progress},
            message=message or f"Progress: {progress * 100:.1f}%",
            severity="info",
        )

    @classmethod
    def create_tool_use(
        cls,
        request_id: str,
        tool_name: str,
        tool_input: dict[str, Any],
        parent_id: str | None = None,
    ) -> SubAgentEvent:
        """Factory for TOOL_USE event."""
        return cls(
            request_id=request_id,
            parent_id=parent_id,
            event_type=SubAgentEventType.TOOL_USE,
            payload={"tool_name": tool_name, "tool_input": tool_input},
            message=f"Tool used: {tool_name}",
            severity="debug",
        )

    @classmethod
    def create_error(
        cls,
        request_id: str,
        error: str,
        parent_id: str | None = None,
    ) -> SubAgentEvent:
        """Factory for ERROR event."""
        return cls(
            request_id=request_id,
            parent_id=parent_id,
            event_type=SubAgentEventType.ERROR,
            payload={"error": error},
            message=error,
            severity="error",
        )

    @classmethod
    def create_completed(
        cls,
        request_id: str,
        output: dict[str, Any],
        parent_id: str | None = None,
    ) -> SubAgentEvent:
        """Factory for COMPLETED event."""
        return cls(
            request_id=request_id,
            parent_id=parent_id,
            event_type=SubAgentEventType.COMPLETED,
            payload={"output": output},
            message="Sub-agent completed successfully",
            severity="info",
        )


class SubAgentProtocolSerializer:
    """Handles JSONL serialization for InterAgentProtocol messages.

    Provides utility methods for reading/writing protocol messages
    to/from JSONL files.
    """

    @staticmethod
    def write_request(request: SubAgentRequest, path: Path) -> None:
        """Append a request to a JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(request.to_jsonl())

    @staticmethod
    def write_result(result: SubAgentResult, path: Path) -> None:
        """Append a result to a JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(result.to_jsonl())

    @staticmethod
    def write_event(event: SubAgentEvent, path: Path) -> None:
        """Append an event to a JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(event.to_jsonl())

    @staticmethod
    def read_requests(path: Path) -> list[SubAgentRequest]:
        """Read all requests from a JSONL file."""
        requests = []
        if not path.exists():
            return requests
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    requests.append(SubAgentRequest.from_jsonl(line))
        return requests

    @staticmethod
    def read_results(path: Path) -> list[SubAgentResult]:
        """Read all results from a JSONL file."""
        results = []
        if not path.exists():
            return results
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(SubAgentResult.from_jsonl(line))
        return results

    @staticmethod
    def read_events(path: Path) -> list[SubAgentEvent]:
        """Read all events from a JSONL file."""
        events = []
        if not path.exists():
            return events
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(SubAgentEvent.from_jsonl(line))
        return events

    @staticmethod
    def filter_events_by_request(
        events: list[SubAgentEvent],
        request_id: str,
    ) -> list[SubAgentEvent]:
        """Filter events by request ID, maintaining sequence order."""
        return sorted(
            [e for e in events if e.request_id == request_id],
            key=lambda e: e.sequence,
        )


__all__ = [
    "SubAgentEvent",
    "SubAgentEventType",
    "SubAgentProtocolSerializer",
    "SubAgentRequest",
    "SubAgentResult",
    "SubAgentStatus",
]
