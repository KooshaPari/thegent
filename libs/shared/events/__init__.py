"""
Phenotype Shared Events Library
================================

Provides unified event handling patterns across the Phenotype ecosystem,
supporting both local and distributed (cloud/Dinoforge) event processing.

Architecture
------------
- Event Bus: Decoupled event dispatch with in-process and remote adapters
- Event Store: Append-only event sourcing store
- Event Handlers: Composable event reaction pipeline
- Serializer: JSON/MessagePack for cross-service events

Design Principles
----------------
- Events are facts (immutable past tense naming)
- Strict typing for event payloads
- Event versioning for schema evolution
- At-least-once delivery with idempotent handlers

Compatibility
-------------
- Local: In-process event bus (synchronous)
- Dinoforge: Cloud event adapters (SQS/SNS/Kafka)

Version: 0.1.0 | Status: stub | SemVer: 0.1.0

@architecture
  layer: infrastructure
  pattern: cqrs.event-sourcing
  hex_boundary: outbound
"""

from __future__ import annotations

__version__ = "0.1.0"
__status__ = "stub"
__semver__ = "0.1.0"

# --------------------------------------------------------------------------- #
# Public API Surface                                                            #
# --------------------------------------------------------------------------- #

class Event:
    """
    Base event marker (interface in duck-typed Python).

    Concrete events should:
    - Use past-tense names (UserRegistered, OrderPlaced)
    - Include event_id, occurred_at, metadata fields
    - Be frozen dataclasses for immutability
    """

    event_type: str
    event_id: str
    occurred_at: str  # ISO8601
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "event_id": self.event_id,
            "occurred_at": self.occurred_at,
            "metadata": self.metadata,
        }


class EventHandler:
    """
    Handles events of a specific type.

    Implement handle(event: YourEvent) -> None
    """

    event_type: type[Event]

    def handle(self, event: Event) -> None:
        raise NotImplementedError


class EventBus:
    """
    Dispatches events to registered handlers.

    Supports:
    - In-process (sync) dispatch
    - Remote dispatch (via adapter)
    - Middleware pipeline
    """

    def subscribe(self, handler: EventHandler) -> None:
        raise NotImplementedError

    def publish(self, event: Event) -> None:
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Event Bus Implementations                                                     #
# --------------------------------------------------------------------------- #

class SyncEventBus(EventBus):
    """In-process synchronous event dispatcher."""

    def __init__(self):
        self._handlers: dict[type[Event], list[EventHandler]] = {}

    def subscribe(self, handler: EventHandler) -> None:
        etype = handler.event_type
        self._handlers.setdefault(etype, []).append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers.get(type(event), []):
            handler.handle(event)


class AsyncEventBus(EventBus):
    """Async event dispatcher for background processing."""

    def __init__(self, adapter: str = "in_memory"):
        self._adapter = adapter

    def subscribe(self, handler: EventHandler) -> None:
        raise NotImplementedError("Use remote adapter for async dispatch")

    def publish(self, event: Event) -> None:
        raise NotImplementedError("Use remote adapter for async dispatch")


# --------------------------------------------------------------------------- #
# Event Store (Event Sourcing)                                                  #
# --------------------------------------------------------------------------- #

class EventStore:
    """
    Append-only store for event sourcing.

    Operations:
    - append(event): Store a new event
    - get_stream(aggregate_id): Fetch all events for an aggregate
    - get_all(bucket, start, end): Time-range query
    """

    def append(self, event: Event) -> None:
        raise NotImplementedError

    def get_stream(self, aggregate_id: str) -> list[Event]:
        raise NotImplementedError

    def get_all(self, bucket: str, start: str, end: str) -> list[Event]:
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Cloud Adapter Interfaces (Dinoforge)                                          #
# --------------------------------------------------------------------------- #

class CloudEventAdapter:
    """
    Dinoforge cloud event adapter interface.

    Implementations:
    - SQS adapter (AWS Simple Queue Service)
    - SNS adapter (AWS Simple Notification Service)
    - Kafka adapter (confluent-kafka-python)
    """

    def send(self, event: Event) -> None:
        raise NotImplementedError

    def receive(self) -> Event:
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Utilities                                                                   #
# --------------------------------------------------------------------------- #

def create_event(
    event_type: str,
    payload: dict,
    metadata: dict | None = None,
    event_id: str | None = None,
) -> Event:
    """Factory for creating typed events."""
    from dataclasses import dataclass, field
    from datetime import datetime, timezone
    import uuid

    @dataclass(frozen=True)
    class TypedEvent(Event):
        event_type: str = event_type
        event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
        occurred_at: str = field(
            default_factory=lambda: datetime.now(timezone.utc).isoformat()
        )
        metadata: dict = field(default_factory=lambda: metadata or {})
        payload: dict = field(default_factory=lambda: payload)

        def to_dict(self) -> dict:
            base = super().to_dict()
            base["payload"] = self.payload
            return base

    return TypedEvent()
