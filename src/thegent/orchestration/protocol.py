"""Orchestration protocol definitions."""
from __future__ import annotations
from enum import Enum
from typing import Any


class OrchestrationProtocol:
    """Protocol for orchestration communication."""
    
    def __init__(self) -> None:
        self.version = "1.0"
    
    def encode(self, message: dict[str, Any]) -> bytes:
        """Encode a message."""
        return b""
    
    def decode(self, data: bytes) -> dict[str, Any]:
        """Decode a message."""
        return {"type": "unknown"}


class TaskMessage:
    """A task message in the orchestration protocol."""
    
    def __init__(self, task_id: str, payload: dict[str, Any]) -> None:
        self.task_id = task_id
        self.payload = payload


class SubAgentRequest:
    """Sub-agent request."""
    
    def __init__(self, request_id: str, task: dict[str, Any]) -> None:
        self.request_id = request_id
        self.task = task


class SubAgentResult:
    """Sub-agent result."""
    
    def __init__(self, request_id: str, success: bool, result: Any | None = None) -> None:
        self.request_id = request_id
        self.success = success
        self.result = result


class SubAgentEvent:
    """Sub-agent event."""
    
    def __init__(self, event_type: str, data: dict[str, Any]) -> None:
        self.event_type = event_type
        self.data = data


class SubAgentStatus(Enum):
    """Sub-agent status enumeration."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubAgentEventType(Enum):
    """Sub-agent event type enumeration."""
    
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    LOG = "log"


__all__ = [
    "OrchestrationProtocol",
    "TaskMessage",
    "SubAgentRequest",
    "SubAgentResult",
    "SubAgentEvent",
    "SubAgentStatus",
    "SubAgentEventType",
    "SubAgentProtocolSerializer",
    "get_protocol",
]


def get_protocol() -> OrchestrationProtocol:
    """Get the orchestration protocol instance."""
    return OrchestrationProtocol()


class SubAgentProtocolSerializer:
    """Serializer for sub-agent protocol."""

    def serialize(self, message: SubAgentRequest) -> bytes:
        """Serialize a sub-agent request."""
        return b""

    def deserialize(self, data: bytes) -> SubAgentRequest:
        """Deserialize a sub-agent request."""
        return SubAgentRequest(request_id="", task={})
