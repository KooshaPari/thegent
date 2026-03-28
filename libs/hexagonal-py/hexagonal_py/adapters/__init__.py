"""
Adapters Layer - Infrastructure implementations
"""

from abc import ABC
from typing import TypeVar, Generic, List, Optional, Dict, Set, Any

from ..domain import DomainEvent

T = TypeVar("T")
TId = TypeVar("TId")
E = TypeVar("E", bound=DomainEvent)


# In-Memory Repository
class InMemoryRepository(ABC, Generic[T, TId]):
    """In-memory repository implementation"""

    def __init__(self):
        self._entities: Dict[str, T] = {}

    async def save(self, entity: T) -> T:
        id_str = self._get_id_str(entity)
        self._entities[id_str] = entity
        return entity

    async def find_by_id(self, id: TId) -> Optional[T]:
        id_str = str(id)
        return self._entities.get(id_str)

    async def delete(self, id: TId) -> None:
        id_str = str(id)
        self._entities.pop(id_str, None)

    async def find_all(self) -> List[T]:
        return list(self._entities.values())

    async def exists(self, id: TId) -> bool:
        return str(id) in self._entities

    def clear(self) -> None:
        self._entities.clear()

    def _get_id_str(self, entity: T) -> str:
        """Override in subclass to get ID from entity"""
        return str(getattr(entity, "id", entity))


# REST Adapter
class RestAdapter:
    """REST API adapter"""

    def __init__(self):
        self._routes: Dict[str, callable] = {}

    def register(
        self,
        method: str,
        path: str,
        handler: callable,
    ) -> None:
        key = f"{method.upper()}:{path}"
        self._routes[key] = handler

    async def handle(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        query: dict | None = None,
    ) -> "RestResponse":
        key = f"{method.upper()}:{path}"
        handler = self._routes.get(key)

        if not handler:
            return RestResponse(
                status=404,
                body=None,
                error=RestError(code="NOT_FOUND", message="Route not found"),
            )

        try:
            result = await handler(body=body, query=query or {})
            return RestResponse(status=200, body=result)
        except Exception as e:
            return RestResponse(
                status=500,
                body=None,
                error=RestError(
                    code="INTERNAL_ERROR",
                    message=str(e),
                ),
            )


class RestResponse:
    """REST response"""

    def __init__(
        self,
        status: int,
        body: Any = None,
        error: "RestError | None" = None,
        headers: dict | None = None,
    ):
        self.status = status
        self.body = body
        self.error = error
        self.headers = headers or {}


class RestError:
    """REST error"""

    def __init__(
        self,
        code: str,
        message: str,
        details: Any = None,
    ):
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# Message Bus
class InMemoryMessageBus(Generic[E]):
    """In-memory message bus implementation"""

    def __init__(self):
        self._subscribers: Dict[str, Set[callable]] = {}

    async def publish(self, topic: str, event: E) -> None:
        handlers = self._subscribers.get(topic, set())
        for handler in handlers:
            await handler(event)

    def subscribe(self, topic: str, handler: callable) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(handler)

    def unsubscribe(self, topic: str, handler: callable) -> None:
        if topic in self._subscribers:
            self._subscribers[topic].discard(handler)
