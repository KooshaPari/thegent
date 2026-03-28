"""
Phenotype Telemetry Core - Distributed Tracing Abstractions

Provides OpenTelemetry-compatible tracing interfaces for the ecosystem.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading


class SpanContext:
    """Context for a distributed trace span."""
    
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
        is_sampled: bool = True
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.is_sampled = is_sampled
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "is_sampled": self.is_sampled,
        }


class SpanKind:
    """Kind of span (producer, consumer, client, server, internal)."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus:
    """Status of a span."""
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class Span(ABC):
    """Abstract distributed trace span."""
    
    @property
    @abstractmethod
    def context(self) -> SpanContext:
        """Get the span context."""
        pass
    
    @abstractmethod
    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        pass
    
    @abstractmethod
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """Set multiple span attributes."""
        pass
    
    @abstractmethod
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        pass
    
    @abstractmethod
    def set_status(self, status: str, description: Optional[str] = None) -> None:
        """Set the span status."""
        pass
    
    @abstractmethod
    def record_exception(self, exception: Exception) -> None:
        """Record an exception in the span."""
        pass
    
    @abstractmethod
    def end(self) -> None:
        """End the span."""
        pass


class Tracer(ABC):
    """Abstract distributed tracer."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the tracer name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> Optional[str]:
        """Get the tracer version."""
        pass
    
    @abstractmethod
    def start_span(
        self,
        name: str,
        kind: str = SpanKind.INTERNAL,
        parent_context: Optional[SpanContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """Start a new span."""
        pass
    
    @abstractmethod
    def create_span(self, name: str, **kwargs) -> Span:
        """Create a new span (alias for start_span)."""
        pass


class NoOpSpan(Span):
    """No-operation span implementation."""
    
    def __init__(self):
        self._context = SpanContext(
            trace_id="00000000000000000000000000000000",
            span_id="0000000000000000",
        )
    
    @property
    def context(self) -> SpanContext:
        return self._context
    
    def set_attribute(self, key: str, value: Any) -> None:
        pass
    
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        pass
    
    def set_status(self, status: str, description: Optional[str] = None) -> None:
        pass
    
    def record_exception(self, exception: Exception) -> None:
        pass
    
    def end(self) -> None:
        pass


class NoOpTracer(Tracer):
    """No-operation tracer implementation."""
    
    @property
    def name(self) -> str:
        return "noop"
    
    @property
    def version(self) -> Optional[str]:
        return None
    
    def start_span(
        self,
        name: str,
        kind: str = SpanKind.INTERNAL,
        parent_context: Optional[SpanContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        return NoOpSpan()
    
    def create_span(self, name: str, **kwargs) -> Span:
        return NoOpSpan()


# Global tracer provider
_tracer_provider: Optional['TracerProvider'] = None
_provider_lock = threading.Lock()


class TracerProvider(ABC):
    """Abstract tracer provider."""
    
    @abstractmethod
    def get_tracer(self, name: str, version: Optional[str] = None) -> Tracer:
        """Get a tracer by name and version."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the provider."""
        pass


def get_tracer(name: str, version: Optional[str] = None) -> Tracer:
    """Get the global tracer."""
    global _tracer_provider
    with _provider_lock:
        if _tracer_provider is None:
            return NoOpTracer()
        return _tracer_provider.get_tracer(name, version)


def set_tracer_provider(provider: TracerProvider) -> None:
    """Set the global tracer provider."""
    global _tracer_provider
    with _provider_lock:
        _tracer_provider = provider


def create_span(name: str, **kwargs) -> Span:
    """Convenience function to create a span from the global tracer."""
    tracer = get_tracer("phenotype")
    return tracer.start_span(name, **kwargs)


__all__ = [
    "Span",
    "SpanContext",
    "SpanKind",
    "SpanStatus",
    "Tracer",
    "TracerProvider",
    "NoOpSpan",
    "NoOpTracer",
    "get_tracer",
    "set_tracer_provider",
    "create_span",
]
