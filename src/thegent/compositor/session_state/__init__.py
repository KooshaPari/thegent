"""Stub module."""
from typing import Any


class SessionState:
    """Session state for compositor."""

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        """Get state value."""
        return self._state.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value


__all__ = ["SessionState"]
