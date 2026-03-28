"""
Shared Hexagonal Architecture Library

Provides reusable ports and base implementations for hexagonal architecture
across the Phenotype ecosystem.

Modules:
    - ports.inbound: Input port interfaces (use case definitions)
    - ports.outbound: Output port interfaces (external dependency contracts)
    - base: Base classes for domain entities, value objects, and events
    - exceptions: Shared hexagonal architecture exceptions
"""

from typing import TypeVar, Protocol

# Generic type for domain entities
T = TypeVar("T")


class DomainEntity(Protocol):
    """Protocol for all domain entities in hexagonal architecture."""
    
    @property
    def id(self) -> str:
        """Unique identifier for the entity."""
        ...
    
    def to_primitive(self) -> dict:
        """Convert entity to primitive dict representation."""
        ...


class ValueObject(Protocol):
    """Protocol for all value objects in hexagonal architecture."""
    
    def equals(self, other: object) -> bool:
        """Value equality check."""
        ...
    
    def to_primitive(self) -> dict:
        """Convert value object to primitive dict representation."""
        ...


class DomainEvent(Protocol):
    """Protocol for all domain events."""
    
    @property
    def event_type(self) -> str:
        """Type identifier for the event."""
        ...
    
    @property
    def occurred_at(self) -> str:
        """ISO 8601 timestamp when event occurred."""
        ...
    
    def to_primitive(self) -> dict:
        """Convert event to primitive dict representation."""
        ...


class InputPort(Protocol[T]):
    """Protocol for input ports (use cases)."""
    
    async def execute(self, *args, **kwargs) -> T:
        """Execute the use case."""
        ...


class OutputPort(Protocol):
    """Protocol for output ports (external dependencies)."""
    ...


class Repository(Protocol[T]):
    """Protocol for repository pattern implementation."""
    
    async def save(self, entity: T) -> None:
        """Persist an entity."""
        ...
    
    async def find_by_id(self, id: str) -> T | None:
        """Find entity by unique identifier."""
        ...
    
    async def find_all(self, **filters) -> list[T]:
        """Find all entities matching filters."""
        ...
    
    async def delete(self, id: str) -> None:
        """Delete entity by identifier."""
        ...


__all__ = [
    "DomainEntity",
    "ValueObject", 
    "DomainEvent",
    "InputPort",
    "OutputPort",
    "Repository",
]
