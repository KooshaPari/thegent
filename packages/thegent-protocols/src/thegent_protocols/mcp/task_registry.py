"""FastMCP task mode support for thegent.

Provides an asyncio-based task registry that allows long-running MCP tool calls
to be tracked, status-polled, and cancelled by MCP clients.

Usage:
    # Wrap a long-running call as a background task
    task_id = _TASK_REGISTRY.create(asyncio.create_task(some_coroutine()))

    # Client polls status
    status = _TASK_REGISTRY.status(task_id)

    # Client cancels
    _TASK_REGISTRY.cancel(task_id)

The registry is module-level (process singleton) and is safe for concurrent
asyncio access.  It does NOT persist across process restarts.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    import asyncio

_log = logging.getLogger(__name__)

TaskStatus = Literal["running", "done", "error", "cancelled"]


class _TaskEntry:
    """Internal record for a tracked asyncio task."""

    __slots__ = ("message", "progress", "started_at", "task", "task_id", "total")

    def __init__(self, task_id: str, task: asyncio.Task[Any]) -> None:
        self.task_id = task_id
        self.task = task
        self.started_at = time.time()
        self.progress: float = 0.0
        self.total: float | None = None
        self.message: str = ""


class AsyncTaskRegistry:
    """Registry mapping task_id -> asyncio.Task with status/progress tracking.

    Thread-safety: this class is designed for asyncio single-threaded use.
    All mutations happen within the event loop; no locks are required.
    """

    def __init__(self) -> None:
        self._entries: dict[str, _TaskEntry] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(self, task: asyncio.Task[Any], task_id: str | None = None) -> str:
        """Register a running asyncio task and return its task_id."""
        tid = task_id or f"mcp-task-{uuid.uuid4().hex[:12]}"
        entry = _TaskEntry(tid, task)
        self._entries[tid] = entry
        _log.debug("task_registry: created task_id=%s", tid)
        return tid

    def update_progress(self, task_id: str, progress: float, total: float | None = None, message: str = "") -> None:
        """Update progress metadata for an in-flight task (called from within the task)."""
        entry = self._entries.get(task_id)
        if entry is not None:
            entry.progress = progress
            if total is not None:
                entry.total = total
            if message:
                entry.message = message

    def status(self, task_id: str) -> dict[str, Any]:
        """Return status dict for task_id.

        Returns:
            {
                "task_id": str,
                "status": "running" | "done" | "error" | "cancelled",
                "progress": float,
                "total": float | None,
                "message": str,
                "result": Any | None,   # only when done
                "error": str | None,    # only when error
                "elapsed_s": float,
            }
        """
        entry = self._entries.get(task_id)
        if entry is None:
            return {"task_id": task_id, "status": "not_found", "error": f"Unknown task_id: {task_id}"}

        task = entry.task
        elapsed = time.time() - entry.started_at
        base: dict[str, Any] = {
            "task_id": task_id,
            "progress": entry.progress,
            "total": entry.total,
            "message": entry.message,
            "elapsed_s": round(elapsed, 2),
            "result": None,
            "error": None,
        }

        if task.cancelled():
            return {**base, "status": "cancelled"}
        if task.done():
            exc = task.exception()
            if exc is not None:
                return {**base, "status": "error", "error": str(exc)}
            return {**base, "status": "done", "result": task.result()}
        return {**base, "status": "running"}

    def cancel(self, task_id: str) -> dict[str, Any]:
        """Request cancellation of a running task.

        Returns:
            {"task_id": str, "cancelled": bool, "status": str}
        """
        entry = self._entries.get(task_id)
        if entry is None:
            return {"task_id": task_id, "cancelled": False, "status": "not_found"}

        task = entry.task
        if task.done():
            return {"task_id": task_id, "cancelled": False, "status": self.status(task_id)["status"]}

        task.cancel()
        _log.debug("task_registry: cancelled task_id=%s", task_id)
        return {"task_id": task_id, "cancelled": True, "status": "cancelling"}

    def list_tasks(self) -> list[dict[str, Any]]:
        """Return status summary for all tracked tasks."""
        return [self.status(tid) for tid in list(self._entries)]

    def cleanup(self, max_age_s: float = 3600.0) -> int:
        """Remove completed tasks older than max_age_s seconds. Returns count removed."""
        now = time.time()
        to_remove = [
            tid for tid, entry in self._entries.items() if entry.task.done() and (now - entry.started_at) > max_age_s
        ]
        for tid in to_remove:
            del self._entries[tid]
        return len(to_remove)


# Module-level singleton used by mcp_server.py tool registrations
_TASK_REGISTRY = AsyncTaskRegistry()


def get_task_registry() -> AsyncTaskRegistry:
    """Return the process-singleton AsyncTaskRegistry."""
    return _TASK_REGISTRY
