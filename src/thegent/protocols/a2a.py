"""GW-67: Agent-to-Agent (A2A) protocol support.

Implements the A2A message format for inter-agent communication.
Allows thegent to act as an A2A gateway, routing agent messages
to appropriate LLM backends.

A2A message format:
{
  "id": "<uuid>",
  "source_agent": "agent-A",
  "target_agent": "agent-B",
  "message_type": "request" | "response" | "event" | "error",
  "payload": {...},
  "metadata": {...},
  "timestamp": <unix_float>,
  "correlation_id": "<uuid>"  # links request->response
}

# @trace FR-PROTO-067
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable

_log = logging.getLogger(__name__)

VALID_MESSAGE_TYPES: frozenset[str] = frozenset({"request", "response", "event", "error"})


@dataclass
class A2AMessage:
    """Represents an Agent-to-Agent protocol message."""

    source_agent: str
    target_agent: str
    message_type: str  # "request" | "response" | "event" | "error"
    payload: dict
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""


def validate_a2a_message(msg: A2AMessage) -> list[str]:
    """Validate an A2A message. Returns list of validation errors (empty = valid)."""
    errors: list[str] = []

    if not msg.source_agent:
        errors.append("source_agent must not be empty")

    if not msg.target_agent:
        errors.append("target_agent must not be empty")

    if msg.message_type not in VALID_MESSAGE_TYPES:
        errors.append(f"message_type must be one of {sorted(VALID_MESSAGE_TYPES)!r}, got {msg.message_type!r}")

    if not isinstance(msg.payload, dict):
        errors.append("payload must be a dict")

    if not isinstance(msg.metadata, dict):
        errors.append("metadata must be a dict")

    if not msg.id:
        errors.append("id must not be empty")

    return errors


def a2a_message_from_dict(data: dict) -> A2AMessage:
    """Deserialize an A2A message from a dict. Raises ValueError on missing required fields."""
    required = ("source_agent", "target_agent", "message_type", "payload")
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"A2AMessage missing required fields: {missing}")

    return A2AMessage(
        source_agent=data["source_agent"],
        target_agent=data["target_agent"],
        message_type=data["message_type"],
        payload=data["payload"],
        id=data.get("id", str(uuid.uuid4())),
        metadata=data.get("metadata", {}),
        timestamp=data.get("timestamp", time.time()),
        correlation_id=data.get("correlation_id", ""),
    )


def a2a_message_to_dict(msg: A2AMessage) -> dict:
    """Serialize an A2A message to a JSON-serializable dict."""
    return {
        "id": msg.id,
        "source_agent": msg.source_agent,
        "target_agent": msg.target_agent,
        "message_type": msg.message_type,
        "payload": msg.payload,
        "metadata": msg.metadata,
        "timestamp": msg.timestamp,
        "correlation_id": msg.correlation_id,
    }


def create_response(
    request: A2AMessage,
    source_agent: str,
    payload: dict,
    *,
    error: str = "",
) -> A2AMessage:
    """Create a response message correlated to a request."""
    message_type = "error" if error else "response"
    response_payload = dict(payload)
    if error:
        response_payload["error"] = error

    return A2AMessage(
        source_agent=source_agent,
        target_agent=request.source_agent,
        message_type=message_type,
        payload=response_payload,
        correlation_id=request.id,
    )


class A2ARouter:
    """Routes A2A messages to registered handler functions."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[A2AMessage], A2AMessage | None]]] = {}
        self._lock: threading.Lock = threading.Lock()

    def register(self, target_agent: str, handler: Callable[[A2AMessage], A2AMessage | None]) -> None:
        """Register a handler for messages targeting target_agent."""
        with self._lock:
            if target_agent not in self._handlers:
                self._handlers[target_agent] = []
            self._handlers[target_agent].append(handler)
        _log.debug("Registered handler for agent %r", target_agent)

    def unregister(self, target_agent: str) -> None:
        """Remove all handlers for target_agent."""
        with self._lock:
            self._handlers.pop(target_agent, None)
        _log.debug("Unregistered handlers for agent %r", target_agent)

    def route(self, msg: A2AMessage) -> list[A2AMessage]:
        """Route message to registered handlers. Returns list of response messages."""
        with self._lock:
            handlers = list(self._handlers.get(msg.target_agent, []))

        if not handlers:
            _log.debug("No handlers registered for target agent %r", msg.target_agent)
            return []

        responses: list[A2AMessage] = []
        for handler in handlers:
            try:
                result = handler(msg)
                if result is not None:
                    responses.append(result)
            except Exception:
                _log.exception("Handler for agent %r raised an exception", msg.target_agent)

        return responses

    def list_agents(self) -> list[str]:
        """Return sorted list of registered target agent names."""
        with self._lock:
            return sorted(self._handlers.keys())
