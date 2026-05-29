"""Stub module."""
from __future__ import annotations


class QueueStorage:
    """Storage for queue."""

    def __init__(self) -> None:
        self._storage: dict = {}

    def push(self, queue: str, item: dict) -> None:
        if queue not in self._storage:
            self._storage[queue] = []
        self._storage[queue].append(item)

    def pop(self, queue: str) -> dict | None:
        if self._storage.get(queue):
            return self._storage[queue].pop(0)
        return None


__all__ = ["QueueStorage", "PromptQueue"]


class PromptQueue:
    """Queue for prompts."""

    def __init__(self) -> None:
        self._queue: list = []

    def enqueue(self, prompt: dict) -> None:
        """Enqueue a prompt."""
        self._queue.append(prompt)

    def dequeue(self) -> dict | None:
        """Dequeue a prompt."""
        if self._queue:
            return self._queue.pop(0)
        return None

    def peek(self) -> dict | None:
        """Peek at the next prompt without dequeuing."""
        if self._queue:
            return self._queue[0]
        return None

    def size(self) -> int:
        """Get the size of the queue."""
        return len(self._queue)
