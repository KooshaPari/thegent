"""
Adapter Port Interface - Unified Adapter Pattern

Defines port interfaces for all adapters in thegent.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol

class AdapterPort(Protocol):
    """Protocol all adapters must implement"""
    
    def call(self, **kwargs) -> dict[str, Any]:
        ...


class HTTPAdapter(AdapterPort):
    """HTTP proxy adapter"""
    @abstractmethod
    def proxy_request(self, request: Any) -> Any: ...

class EventAdapter(AdapterPort):
    """Event bus adapter"""
    @abstractmethod
    def emit(self, event: str, data: dict): ...
    @abstractmethod
    def subscribe(self, event: str, handler): ...

class StorageAdapter(Port):
    """Storage abstraction"""
    @abstractmethod
    def save(self, key: str, value: Any): ...
    @abstractmethod
    def load(self, key: str) -> Any: ...

# Unified adapter registry
class AdapterRegistry:
    _adapters: dict[str, AdapterPort] = {}
    
    @classmethod
    def register(cls, name: str, adapter: AdapterPort):
        cls._adapters[name] = adapter
    
    @classmethod
    def get(cls, name: str) -> AdapterPort:
        return cls._adapters.get(name)
    
    @classmethod
    def all(cls) -> dict[str, AdapterPort]:
        return cls._adapters.copy()
