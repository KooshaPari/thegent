"""Minimal Context stub for vendored opentelemetry.

FastMCP imports opentelemetry.context.Context; this provides a compatible
placeholder when using the project's vendored trace/sdk stubs.
"""

from typing import Any


class Context:
    """Minimal Context stub for distributed trace context propagation."""

    def __init__(self, values: dict[str, Any | None] | None = None) -> None:
        self._values = dict(values) if values else {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def copy(self) -> dict[str, Any]:
        return self._values.copy()

    def __contains__(self, key: str) -> bool:
        return key in self._values


__all__ = ["Context"]
