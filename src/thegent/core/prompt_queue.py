"""PromptQueueManager: project-aware unified prompt queue (FR-HAX-001).

Stores tasks in `.thegent/prompt_queue.jsonl` relative to the project root,
falling back to `~/.thegent/prompt_queue.jsonl` when outside a project.

Fields: timestamp, prompt, project_path, status (pending/claimed/done), id (ulid), metadata.

# @trace FR-HAX-001
"""

from __future__ import annotations

import orjson as json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.integrations.base import SerializableMixin
from thegent.queue.locking import QueueLock

logger = logging.getLogger(__name__)

_QUEUE_FILENAME = "prompt_queue.jsonl"
_THEGENT_DIR = ".thegent"


def _generate_ulid() -> str:
    """Generate a ULID-like ID using timestamp (ms) + random bits via os.urandom.

    Format: 26 chars, Crockford base32 alphabet.
    Compatible with standard ULID sort ordering.
    """
    import base64

    ts_ms = int(time.time() * 1000)
    # 10 bytes = 80 bits; we encode with standard base64 then trim
    random_bytes = os.urandom(10)
    # Pack: 6-byte big-endian ms timestamp + 10 random bytes = 16 bytes total
    ts_bytes = ts_ms.to_bytes(6, "big")
    raw = ts_bytes + random_bytes
    # Base64-encode and strip padding for a URL-safe, lexicographically sorted ID
    encoded = base64.b32encode(raw).decode("ascii").rstrip("=")
    return encoded[:26].upper()


def _find_project_queue_path(project_path: str | None = None) -> Path:
    """Resolve the queue file path.

    Priority:
    1. `project_path/.thegent/prompt_queue.jsonl` if provided and `.thegent/` exists.
    2. `cwd/.thegent/prompt_queue.jsonl` if `.thegent/` exists in cwd.
    3. `~/.thegent/prompt_queue.jsonl` as global fallback.
    """
    if project_path:
        candidate = Path(project_path) / _THEGENT_DIR / _QUEUE_FILENAME
        if candidate.parent.exists() or (Path(project_path) / _THEGENT_DIR).exists():
            return candidate

    cwd_candidate = Path.cwd() / _THEGENT_DIR / _QUEUE_FILENAME
    if (Path.cwd() / _THEGENT_DIR).exists():
        return cwd_candidate

    return Path.home() / _THEGENT_DIR / _QUEUE_FILENAME


@dataclass
class QueueItem(SerializableMixin):
    """A single item in the prompt queue.

    # @trace FR-HAX-001
    """

    id: str
    """ULID identifier, lexicographically sortable by creation time."""

    timestamp: str
    """ISO-8601 creation timestamp (UTC)."""

    prompt: str
    """The task prompt text."""

    project_path: str
    """Absolute path to the project this task belongs to."""

    status: str
    """One of: pending, claimed, done."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Structured metadata for queue consumers (for example vetter revision details)."""

    extra: dict[str, Any] = field(default_factory=dict)
    """Any additional metadata stored in the queue entry."""

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dict for JSONL storage - includes extra fields at top level."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "project_path": self.project_path,
            "status": self.status,
            "metadata": self.metadata,
            **self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QueueItem:
        """Deserialise from a stored JSONL dict."""
        known = {"id", "timestamp", "prompt", "project_path", "status", "metadata"}
        extra = {k: v for k, v in data.items() if k not in known}
        metadata_value = data.get("metadata", {})
        if not isinstance(metadata_value, dict):
            metadata_value = {}
        return cls(
            id=data.get("id", _generate_ulid()),
            timestamp=data.get("timestamp", datetime.now(UTC).isoformat()),
            prompt=data.get("prompt", ""),
            project_path=data.get("project_path", ""),
            status=data.get("status", "pending"),
            metadata=metadata_value,
            extra=extra,
        )


class PromptQueueManager:
    """Project-aware unified prompt queue (FR-HAX-001).

    Persists tasks to `.thegent/prompt_queue.jsonl` (or `~/.thegent/`).
    Uses advisory file locking for atomic claim operations.

    Example::

        mgr = PromptQueueManager()
        mgr.enqueue("Refactor auth module", project_path="/projects/myapp")
        item = mgr.claim()
        if item:
            # ... do work ...
            mgr.complete(item.id)
    """

    def __init__(self, queue_path: Path | None = None, project_path: str | None = None) -> None:
        """Initialise the manager.

        Args:
            queue_path: Explicit path to the queue file. When None, the path is
                resolved automatically from ``project_path`` or the cwd.
            project_path: Hint for resolving the project-local queue path.
        """
        self.queue_path = queue_path or _find_project_queue_path(project_path)
        logger.debug("PromptQueueManager: queue_path=%s", self.queue_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_all(self) -> list[QueueItem]:
        """Read all items from the queue file."""
        if not self.queue_path.exists():
            return []
        items: list[QueueItem] = []
        with self.queue_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    items.append(QueueItem.from_dict(data))
                except (json.JSONDecodeError, KeyError):
                    logger.warning("PromptQueueManager: skipping malformed line")
        return items

    def _write_all(self, items: list[QueueItem]) -> None:
        """Write all items back to the queue file (full rewrite)."""
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("w", encoding="utf-8") as fh:
            for item in items:
                fh.write(json.dumps(item.to_dict().decode()) + "\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enqueue(
        self,
        prompt: str,
        project_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> QueueItem:
        """Add a new task to the queue.

        Args:
            prompt: The task prompt text.
            project_path: The project this task belongs to. Defaults to cwd.
            metadata: Optional structured metadata persisted with the queue item.

        Returns:
            The newly created QueueItem.

        # @trace FR-HAX-001
        """
        resolved_project = project_path or str(Path.cwd())
        item = QueueItem(
            id=_generate_ulid(),
            timestamp=datetime.now(UTC).isoformat(),
            prompt=prompt,
            project_path=resolved_project,
            status="pending",
            metadata=metadata or {},
        )
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item.to_dict().decode()) + "\n")
        logger.debug("PromptQueueManager.enqueue: id=%r prompt=%r", item.id, prompt[:80])
        return item

    def claim(self) -> QueueItem | None:
        """Atomically claim the first pending item.

        Returns the claimed QueueItem or None if the queue is empty.

        # @trace FR-HAX-001
        """
        with QueueLock(self.queue_path) as lock:
            raw_entries: list[dict[str, Any]] = lock.read_entries()
            items = [QueueItem.from_dict(e) for e in raw_entries]
            for item in items:
                if item.status == "pending":
                    item.status = "claimed"
                    lock.write_entries([i.to_dict() for i in items])
                    logger.debug("PromptQueueManager.claim: claimed id=%r", item.id)
                    return item
        return None

    def complete(self, item_id: str) -> bool:
        """Mark a queue item as done.

        Args:
            item_id: The ULID of the item to complete.

        Returns:
            True if the item was found and updated, False otherwise.

        # @trace FR-HAX-001
        """
        with QueueLock(self.queue_path) as lock:
            raw_entries: list[dict[str, Any]] = lock.read_entries()
            items = [QueueItem.from_dict(e) for e in raw_entries]
            for item in items:
                if item.id == item_id:
                    item.status = "done"
                    lock.write_entries([i.to_dict() for i in items])
                    logger.debug("PromptQueueManager.complete: id=%r", item_id)
                    return True
        return False

    def list_pending(self) -> list[QueueItem]:
        """Return all pending (unclaimed) items, oldest first.

        # @trace FR-HAX-001
        """
        return [item for item in self._read_all() if item.status == "pending"]

    def list_all(self, include_done: bool = False) -> list[QueueItem]:
        """Return all items, optionally including done items."""
        items = self._read_all()
        if include_done:
            return items
        return [item for item in items if item.status != "done"]
