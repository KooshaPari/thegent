"""
Inbound Ports

Inbound ports define how external actors (users, other systems) interact
with the application. They are the driving ports in hexagonal architecture.

Following CQRS pattern:
- Command: Intent to change state (Create, Update, Delete)
- Query: Intent to read state (Get, List, Search)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Optional
from datetime import datetime

T = TypeVar('T')
C = TypeVar('C', bound='Command')
Q = TypeVar('Q', bound='Query')


@dataclass
class Command(ABC):
    """
    Base class for all commands.

    Commands represent intent to perform an action. They should be:
    - Self-contained: Include all necessary data
    - Validated: Validate input before execution
    - Immutable: Commands don't change after creation
    """
    command_id: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if not self.command_id:
            import uuid
            object.__setattr__(self, 'command_id', str(uuid.uuid4()))
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


@dataclass
class Query(ABC):
    """
    Base class for all queries.

    Queries represent intent to read data. They should be:
    - Self-contained: Include all filter/pagination data
    - Read-only: Never modify state
    - Cached: Results can be cached
    """
    query_id: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if not self.query_id:
            import uuid
            object.__setattr__(self, 'query_id', str(uuid.uuid4()))
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


class CommandHandler(ABC, Generic[C]):
    """
    Interface for command handlers.

    Following Single Responsibility Principle:
    - Each handler handles one command type
    - Handlers orchestrate the business logic
    """

    @abstractmethod
    async def handle(self, command: C) -> "CommandResult":
        """
        Handle the command and return the result.

        Args:
            command: The command to handle

        Returns:
            CommandResult with success status and data
        """
        pass


class QueryHandler(ABC, Generic[Q]):
    """
    Interface for query handlers.

    Following CQRS:
    - Separate read and write models
    - Query handlers never modify state
    """

    @abstractmethod
    async def handle(self, query: Q) -> "QueryResult":
        """
        Handle the query and return the result.

        Args:
            query: The query to handle

        Returns:
            QueryResult with data
        """
        pass


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    command_id: str = ""

    @classmethod
    def ok(cls, data: Any = None, command_id: str = "") -> "CommandResult":
        return cls(success=True, data=data, command_id=command_id)

    @classmethod
    def error(cls, error: str, data: Any = None) -> "CommandResult":
        return cls(success=False, error=error, data=data)


@dataclass
class QueryResult:
    """Result of query execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    query_id: str = ""
    total: int = 0
    page: int = 1
    page_size: int = 10

    @classmethod
    def ok(cls, data: Any, query_id: str = "", total: int = 0) -> "QueryResult":
        return cls(success=True, data=data, query_id=query_id, total=total)

    @classmethod
    def error(cls, error: str) -> "QueryResult":
        return cls(success=False, error=error)

    @classmethod
    def paginated(
        cls, data: list, total: int, page: int = 1, page_size: int = 10
    ) -> "QueryResult":
        return cls(
            success=True,
            data=data,
            total=total,
            page=page,
            page_size=page_size,
        )
