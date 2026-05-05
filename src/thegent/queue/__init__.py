"""Stub module."""


class Queue:
    """Simple queue implementation."""

    def __init__(self) -> None:
        self._items: list = []

    def put(self, item: object) -> None:
        """Add item to queue."""
        self._items.append(item)

    def get(self) -> object | None:
        """Get item from queue."""
        if self._items:
            return self._items.pop(0)
        return None


__all__ = ["Queue"]
