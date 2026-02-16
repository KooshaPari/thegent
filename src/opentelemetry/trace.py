from contextlib import contextmanager
from typing import Any

_tracer_provider: Any = None

class Span:
    def __init__(self, name: str) -> None:
        self.name = name

    def set_attribute(self, key: str, value: object) -> None:
        setattr(self, key, value)

    def add_event(self, name: str, attributes: dict | None = None) -> None:
        return None

class Tracer:
    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        span = Span(name)
        yield span

class SpanKind:
    CLIENT = "client"

def get_tracer(name: str) -> Tracer:
    return Tracer()

def get_tracer_provider() -> Any:
    return _tracer_provider

def set_tracer_provider(provider: Any) -> None:
    global _tracer_provider
    _tracer_provider = provider
