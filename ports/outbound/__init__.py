"""
Outbound Ports

Outbound ports define how the application interacts with external services.
They are the driven ports in hexagonal architecture.

Following Dependency Inversion Principle:
- Ports are interfaces (abstractions)
- Adapters implement these interfaces (details)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any, Protocol, runtime_checkable
from datetime import timedelta

# Forward reference for domain events (avoid circular imports)
class DomainEvent:
    """Placeholder for domain events - import from domain.events for full definition."""
    pass

class EventEnvelope:
    """Placeholder for event envelope - import from domain.events for full definition."""
    pass

class Identifier:
    """Placeholder for identifiers - import from domain.entities for full definition."""
    pass


# Type variable for entities
E = TypeVar('E')


class Repository(ABC, Generic[E]):
    """
    Repository interface for persisting entities.

    Following DDD principles:
    - Abstracts persistence details
    - Provides collection-like interface
    - Supports domain-driven design

    Implementations should provide:
    - CRUD operations
    - Query methods
    - Transaction support
    """

    @abstractmethod
    async def save(self, entity: E) -> E:
        """Save an entity and return it."""
        pass

    @abstractmethod
    async def find_by_id(self, id: Any) -> Optional[E]:
        """Find an entity by its ID."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> list[E]:
        """Find all entities with pagination."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity by its ID."""
        pass

    @abstractmethod
    async def exists(self, id: Any) -> bool:
        """Check if an entity exists."""
        pass


class EventBus(ABC):
    """
    Event bus interface for publishing domain events.

    Following Event-Driven Architecture:
    - Decouples event producers from consumers
    - Supports synchronous and asynchronous publishing
    - Enables event sourcing patterns
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        pass

    @abstractmethod
    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type."""
        pass


class Cache(ABC, Generic[E]):
    """
    Cache interface for storing frequently accessed data.

    Following caching patterns:
    - Key-value store abstraction
    - TTL support
    - Cache-aside pattern
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[E]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: E, ttl: Optional[timedelta] = None) -> None:
        """Set a value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass


class EventStore(ABC):
    """
    Event store interface for event sourcing.

    Following Event Sourcing:
    - Stores events instead of state
    - Enables full audit trail
    - Supports replay and projections
    """

    @abstractmethod
    async def append(self, event: DomainEvent) -> None:
        """Append an event to the store."""
        pass

    @abstractmethod
    async def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        """Get all events for an aggregate."""
        pass

    @abstractmethod
    async def get_events_since(
        self, aggregate_id: str, since: Any
    ) -> list[DomainEvent]:
        """Get events since a specific point."""
        pass


class Logger(ABC):
    """
    Logger interface for application logging.

    Following best practices:
    - Structured logging
    - Log levels
    - Context support
    """

    @abstractmethod
    async def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass

    @abstractmethod
    async def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass

    @abstractmethod
    async def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    async def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        pass


class HttpClient(ABC):
    """
    HTTP client interface for external API calls.

    Following interface segregation:
    - Simple interface for HTTP operations
    - Supports GET, POST, PUT, DELETE
    """

    @abstractmethod
    async def get(self, url: str, headers: Optional[dict] = None) -> dict:
        """Perform GET request."""
        pass

    @abstractmethod
    async def post(self, url: str, data: dict, headers: Optional[dict] = None) -> dict:
        """Perform POST request."""
        pass

    @abstractmethod
    async def put(self, url: str, data: dict, headers: Optional[dict] = None) -> dict:
        """Perform PUT request."""
        pass

    @abstractmethod
    async def delete(self, url: str, headers: Optional[dict] = None) -> dict:
        """Perform DELETE request."""
        pass


class FileSystem(ABC):
    """
    File system interface for file operations.

    Abstraction for file operations to enable testing.
    """

    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read file contents."""
        pass

    @abstractmethod
    async def write(self, path: str, contents: bytes) -> None:
        """Write file contents."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete a file."""
        pass
