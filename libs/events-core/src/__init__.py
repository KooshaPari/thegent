"""
Phenotype Events Core - Event Sourcing Abstractions

Provides event sourcing and domain event patterns for the ecosystem.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import threading
import uuid


class EventType(Enum):
    """Base event types."""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    SYSTEM = "system"


@dataclass
class EventMetadata:
    """Metadata for domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = EventType.DOMAIN.value
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    version: str = "1.0"
    tags: Dict[str, str] = field(default_factory=dict)


class DomainEvent:
    """Base class for all domain events."""
    
    def __init__(
        self,
        event_type: str,
        aggregate_id: str,
        metadata: Optional[EventMetadata] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.metadata = metadata or EventMetadata()
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "metadata": {
                "event_id": self.metadata.event_id,
                "occurred_at": self.metadata.occurred_at.isoformat(),
                "event_type": self.metadata.event_type,
                "correlation_id": self.metadata.correlation_id,
                "causation_id": self.metadata.causation_id,
                "version": self.metadata.version,
                "tags": self.metadata.tags,
            },
            "data": self.data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        metadata = EventMetadata(
            event_id=data["metadata"]["event_id"],
            occurred_at=datetime.fromisoformat(data["metadata"]["occurred_at"]),
            event_type=data["metadata"]["event_type"],
            correlation_id=data["metadata"].get("correlation_id"),
            causation_id=data["metadata"].get("causation_id"),
            version=data["metadata"].get("version", "1.0"),
            tags=data["metadata"].get("tags", {}),
        )
        return cls(
            event_type=data["event_type"],
            aggregate_id=data["aggregate_id"],
            metadata=metadata,
            data=data.get("data", {}),
        )


class EventStore(ABC):
    """Abstract event store."""
    
    @abstractmethod
    def append(self, event: DomainEvent) -> None:
        """Append an event to the store."""
        pass
    
    @abstractmethod
    def append_batch(self, events: List[DomainEvent]) -> None:
        """Append multiple events to the store."""
        pass
    
    @abstractmethod
    def get_events(
        self,
        aggregate_id: str,
        from_version: Optional[int] = None,
    ) -> List[DomainEvent]:
        """Get events for an aggregate."""
        pass
    
    @abstractmethod
    def get_all_events(
        self,
        from_timestamp: Optional[datetime] = None,
    ) -> List[DomainEvent]:
        """Get all events from a timestamp."""
        pass


class InMemoryEventStore(EventStore):
    """In-memory implementation of event store."""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
        self._lock = threading.Lock()
    
    def append(self, event: DomainEvent) -> None:
        with self._lock:
            self._events.append(event)
    
    def append_batch(self, events: List[DomainEvent]) -> None:
        with self._lock:
            self._events.extend(events)
    
    def get_events(
        self,
        aggregate_id: str,
        from_version: Optional[int] = None,
    ) -> List[DomainEvent]:
        with self._lock:
            events = [e for e in self._events if e.aggregate_id == aggregate_id]
            if from_version is not None:
                events = events[from_version:]
            return events
    
    def get_all_events(
        self,
        from_timestamp: Optional[datetime] = None,
    ) -> List[DomainEvent]:
        with self._lock:
            if from_timestamp is None:
                return list(self._events)
            return [
                e for e in self._events
                if e.metadata.occurred_at >= from_timestamp
            ]


class EventBus(ABC):
    """Abstract event bus for publishing events."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to subscribers."""
        pass
    
    @abstractmethod
    def subscribe(
        self,
        event_type: str,
        handler: 'EventHandler',
    ) -> None:
        """Subscribe to an event type."""
        pass
    
    @abstractmethod
    def unsubscribe(
        self,
        event_type: str,
        handler: 'EventHandler',
    ) -> None:
        """Unsubscribe from an event type."""
        pass


class EventHandler(ABC):
    """Abstract event handler."""
    
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """Handle an event."""
        pass


class InMemoryEventBus(EventBus):
    """In-memory implementation of event bus."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._lock = threading.Lock()
    
    def publish(self, event: DomainEvent) -> None:
        with self._lock:
            handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            handler.handle(event)
    
    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    h for h in self._subscribers[event_type]
                    if h != handler
                ]


# Global instances
_event_store: Optional[EventStore] = None
_event_bus: Optional[EventBus] = None
_init_lock = threading.Lock()


def get_event_store() -> EventStore:
    """Get the global event store."""
    global _event_store
    with _init_lock:
        if _event_store is None:
            _event_store = InMemoryEventStore()
        return _event_store


def set_event_store(store: EventStore) -> None:
    """Set the global event store."""
    global _event_store
    with _init_lock:
        _event_store = store


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    global _event_bus
    with _init_lock:
        if _event_bus is None:
            _event_bus = InMemoryEventBus()
        return _event_bus


def set_event_bus(bus: EventBus) -> None:
    """Set the global event bus."""
    global _event_bus
    with _init_lock:
        _event_bus = bus


def publish_event(event: DomainEvent) -> None:
    """Publish an event to the global bus."""
    bus = get_event_bus()
    bus.publish(event)


def subscribe_to_events(event_type: str, handler: EventHandler) -> None:
    """Subscribe to events of a given type."""
    bus = get_event_bus()
    bus.subscribe(event_type, handler)


__all__ = [
    "EventType",
    "EventMetadata",
    "DomainEvent",
    "EventStore",
    "InMemoryEventStore",
    "EventBus",
    "InMemoryEventBus",
    "EventHandler",
    "get_event_store",
    "set_event_store",
    "get_event_bus",
    "set_event_bus",
    "publish_event",
    "subscribe_to_events",
]
