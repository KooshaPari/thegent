"""
Domain Events

Domain events are immutable records of something that happened in the domain.
They are the primary means of communicating across bounded contexts.

Following DDD and Event Sourcing principles:
- Immutable: Events cannot be changed once created
- Time-ordered: Events have a timestamp
- Descriptive: Event names describe what happened
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json


@dataclass(frozen=True)
class DomainEvent(ABC):
    """
    Base class for all domain events.

    Following Event Sourcing principles:
    - Immutable: Use frozen dataclass
    - Self-contained: Include all relevant data
    - Time-stamped: Automatic timestamp
    """
    event_id: str = field(default_factory=lambda: str(id(object())))
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    @abstractmethod
    def event_type(self) -> str:
        """Return the event type name."""
        pass

    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type(),
            "event_id": self.event_id,
            "occurred_on": self.occurred_on.isoformat(),
            "metadata": self.metadata,
            **self._event_data(),
        }

    @abstractmethod
    def _event_data(self) -> dict:
        """Return event-specific data."""
        pass

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(self.to_dict())


@dataclass(frozen=True)
class EventEnvelope:
    """
    Wrapper for domain events with routing information.

    Used for event bus publishing to ensure proper routing and handling.
    """
    event: DomainEvent
    event_type: str
    occurred_on: datetime
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_event(cls, event: DomainEvent) -> "EventEnvelope":
        return cls(
            event=event,
            event_type=event.event_type(),
            occurred_on=event.occurred_on,
            metadata=event.metadata,
        )

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "occurred_on": self.occurred_on.isoformat(),
            "metadata": self.metadata,
            "data": self.event.to_dict(),
        }


@dataclass(frozen=True)
class EventMetadata:
    """
    Metadata attached to domain events.

    Includes correlation ID, causation ID, and other contextual information.
    """
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    custom: dict = field(default_factory=dict)

    def with_correlation(self, correlation_id: str) -> "EventMetadata":
        """Return new metadata with correlation ID."""
        return EventMetadata(
            correlation_id=correlation_id,
            causation_id=self.causation_id,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            custom=self.custom,
        )

    def with_causation(self, causation_id: str) -> "EventMetadata":
        """Return new metadata with causation ID."""
        return EventMetadata(
            correlation_id=self.correlation_id,
            causation_id=causation_id,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            custom=self.custom,
        )

    def to_dict(self) -> dict:
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            **self.custom,
        }
