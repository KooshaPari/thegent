"""WL-080: InterAgentProtocol — Typed Message Schema.

Provides `InterAgentMessage` (Pydantic v2) and `MessageBus` for structured
in-memory inter-agent communication with asyncio.Queue per subscriber.

# @trace WL-080
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone, UTC
from typing import Any, Literal

from pydantic import BaseModel, Field


class InterAgentMessage(BaseModel):
    """Typed message exchanged between agents on the message bus.

    # @trace WL-080
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    message_type: Literal["task_request", "status_update", "result", "error", "heartbeat"]
    payload: dict[str, Any]
    correlation_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ttl_s: int = 300


class MessageBus:
    """In-memory message bus using asyncio.Queue per subscribed agent.

    API:
        subscribe(agent_id)          -> asyncio.Queue[InterAgentMessage]
        unsubscribe(agent_id)        -> None  (raises KeyError if not subscribed)
        publish(msg)                 -> None  (raises KeyError if recipient not subscribed)
        drain(agent_id, timeout_s)   -> list[InterAgentMessage]

    # @trace WL-080
    """

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[InterAgentMessage]] = {}

    def subscribe(self, agent_id: str) -> asyncio.Queue[InterAgentMessage]:
        """Register *agent_id* and return its dedicated queue.

        If *agent_id* is already subscribed the existing queue is returned.

        # @trace WL-080
        """
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        return self._queues[agent_id]

    def unsubscribe(self, agent_id: str) -> None:
        """Remove *agent_id*'s queue from the bus.

        Raises KeyError if *agent_id* is not subscribed.

        # @trace WL-080
        """
        del self._queues[agent_id]

    def publish(self, msg: InterAgentMessage) -> None:
        """Put *msg* into the queue of its recipient.

        Raises KeyError if *msg.recipient_id* is not subscribed.

        # @trace WL-080
        """
        queue = self._queues[msg.recipient_id]
        queue.put_nowait(msg)

    def drain(
        self,
        agent_id: str,
        timeout_s: float = 1.0,  # noqa: ARG002 -- future async support
    ) -> list[InterAgentMessage]:
        """Return all messages currently in *agent_id*'s queue (non-blocking).

        Raises KeyError if *agent_id* is not subscribed.
        The *timeout_s* parameter is accepted for API compatibility with
        async callers but is not used in this synchronous drain.

        # @trace WL-080
        """
        queue = self._queues[agent_id]
        messages: list[InterAgentMessage] = []
        while not queue.empty():
            messages.append(queue.get_nowait())
        return messages
