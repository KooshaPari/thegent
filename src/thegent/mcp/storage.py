"""FastMCP storage and event store primitives.

Provides persistent key-value storage (backed by diskcache with JSON
serialisation) and a JSONL-backed event store for use by MCP tools.

Values stored in McpStorage are JSON-encoded before being passed to
diskcache, so only JSON-serialisable types are accepted.  This avoids
any concerns when handling tool input.

# @trace FR-MCP-STORAGE-001
"""

from __future__ import annotations

import contextlib
import orjson as json
import logging
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, cast

import diskcache

if TYPE_CHECKING:
    from collections.abc import Iterator

_log = logging.getLogger(__name__)

# Default base directory under ~/.thegent/mcp for storage artefacts.
# Can be overridden via THGENT_MCP_STORAGE_DIR environment variable.
_DEFAULT_STORAGE_BASE = Path("~/.thegent/mcp").expanduser()


def _storage_base() -> Path:
    """Return resolved base directory from settings."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    if settings.mcp_storage_dir:
        return settings.mcp_storage_dir.expanduser().resolve()
    return _DEFAULT_STORAGE_BASE


# ---------------------------------------------------------------------------
# McpStorage
# ---------------------------------------------------------------------------


class McpStorage:
    """Persistent key-value storage for MCP tools, backed by diskcache.

    Values are JSON-encoded before storage so that only safe, JSON-serialisable
    types are accepted.  Keys must be non-empty strings.  Thread-safe;
    diskcache handles its own file locking.

    Usage::

        storage = McpStorage()
        storage.set("my-key", {"foo": "bar"})
        storage.get("my-key")           # -> {"foo": "bar"}
        storage.list_keys(prefix="my")  # -> ["my-key"]
        storage.delete("my-key")        # -> True
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        base = cache_dir or (_storage_base() / "kv")
        base.mkdir(parents=True, exist_ok=True)
        # diskcache.Cache is used purely as a durable key-expiry store.
        # Values are pre-serialised to JSON strings, so diskcache only stores
        # plain str objects — no unsafe serialisation of user-supplied data occurs.
        self._cache: diskcache.Cache = diskcache.Cache(str(base))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if missing / expired."""
        if not key:
            raise ValueError("key must be a non-empty string")
        raw = self._cache.get(key, default=None)
        if raw is None:
            return default
        # Values are stored as JSON strings; decode on read.
        try:
            return json.loads(cast("str", raw))
        except (json.JSONDecodeError, TypeError):
            _log.warning("McpStorage: corrupt value for key %r; returning default", key)
            return default

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store *value* under *key*, with optional *ttl* in seconds.

        *value* must be JSON-serialisable (dict, list, str, int, float, bool,
        or None).  A TypeError is raised if it is not.
        """
        if not key:
            raise ValueError("key must be a non-empty string")
        try:
            encoded = json.dumps(value).decode()
        except (TypeError, ValueError) as exc:
            raise TypeError(f"value for key {key!r} must be JSON-serialisable: {exc}") from exc
        self._cache.set(key, encoded, expire=ttl)

    def delete(self, key: str) -> bool:
        """Delete *key*.  Returns True if the key existed, False otherwise."""
        if not key:
            raise ValueError("key must be a non-empty string")
        return bool(self._cache.delete(key))

    def list_keys(self, prefix: str = "") -> list[str]:
        """Return all keys, optionally filtered to those beginning with *prefix*."""
        all_keys: list[str] = [k for k in self._cache.iterkeys() if isinstance(k, str)]
        if prefix:
            return [k for k in all_keys if k.startswith(prefix)]
        return all_keys

    def clear(self) -> None:
        """Remove all entries from the store."""
        self._cache.clear()

    def close(self) -> None:
        """Close the underlying diskcache (idempotent)."""
        with contextlib.suppress(Exception):
            self._cache.close()


# ---------------------------------------------------------------------------
# McpEventStore
# ---------------------------------------------------------------------------


class McpEventStore:
    """JSONL-backed event store for MCP tool events.

    Each event is a JSON object appended to a single JSONL file.  Events have
    the shape::

        {
            "event_id": "<uuid4>",
            "event_type": "<string>",
            "payload": { ... },
            "ts": <unix float>
        }

    Thread-safe (write lock around JSONL appends; reads are lock-free after
    snapshot).

    Usage::

        store = McpEventStore()
        eid = store.emit("my.event", {"key": "value"})
        store.replay()              # -> [{"event_id": eid, ...}]
        store.get_event(eid)        # -> {"event_id": eid, ...}
    """

    def __init__(self, events_path: Path | None = None) -> None:
        base = events_path or (_storage_base() / "events.jsonl")
        base.parent.mkdir(parents=True, exist_ok=True)
        self._path: Path = base
        self._write_lock = Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_event(self, record: dict[str, Any]) -> None:
        """Append a single event record to the JSONL file (under lock)."""
        line = json.dumps(record, sort_keys=True).decode() + "\n"
        with self._write_lock:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line)

    def _read_all(self) -> list[dict[str, Any]]:
        """Read all events from the JSONL file.  Returns [] if file is missing."""
        if not self._path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    _log.warning("McpEventStore: corrupt JSONL line skipped: %r", line)
        return records

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def emit(self, event_type: str, payload: dict[str, Any]) -> str:
        """Emit an event and return its event_id (UUID4 string).

        Args:
            event_type: Dot-separated event type string (e.g. "storage.set").
            payload: Arbitrary JSON-serialisable dict.

        Returns:
            The generated event_id string.
        """
        if not event_type:
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")
        # Validate payload is JSON-serialisable before touching the file.
        try:
            json.dumps(payload).decode()
        except (TypeError, ValueError) as exc:
            raise TypeError(f"payload must be JSON-serialisable: {exc}") from exc
        event_id = str(uuid.uuid4())
        record: dict[str, Any] = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
            "ts": time.time(),
        }
        self._write_event(record)
        return event_id

    def replay(self, since_event_id: str | None = None) -> list[dict[str, Any]]:
        """Return all events, optionally from (exclusive) *since_event_id* onward.

        Events are returned in emission order.  If *since_event_id* is provided
        but not found, all events are returned.
        """
        all_events = self._read_all()
        if since_event_id is None:
            return all_events
        # Find the index of the event with the given ID, then return everything after it.
        for i, ev in enumerate(all_events):
            if ev.get("event_id") == since_event_id:
                return all_events[i + 1 :]
        # since_event_id not found — return all
        return all_events

    def subscribe(self, event_type: str) -> Iterator[dict[str, Any]]:
        """Yield all stored events that match *event_type*.

        This is a snapshot iterator (not a live tail).  Call repeatedly for
        new events.
        """
        for ev in self._read_all():
            if ev.get("event_type") == event_type:
                yield ev

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Return the event with the given *event_id*, or None if not found."""
        if not event_id:
            return None
        for ev in self._read_all():
            if ev.get("event_id") == event_id:
                return ev
        return None


# ---------------------------------------------------------------------------
# Singletons via a mutable container to avoid module-level global statements
# ---------------------------------------------------------------------------


class _SingletonRegistry:
    """Holds process-level singleton instances in a mutable container."""

    def __init__(self) -> None:
        self._storage: McpStorage | None = None
        self._storage_lock = Lock()
        self._event_store: McpEventStore | None = None
        self._event_store_lock = Lock()

    def get_storage(self) -> McpStorage:
        """Return the McpStorage singleton, creating it on first call."""
        if self._storage is None:
            with self._storage_lock:
                if self._storage is None:
                    self._storage = McpStorage()
        return self._storage

    def get_event_store(self) -> McpEventStore:
        """Return the McpEventStore singleton, creating it on first call."""
        if self._event_store is None:
            with self._event_store_lock:
                if self._event_store is None:
                    self._event_store = McpEventStore()
        return self._event_store

    def reset(
        self,
        storage: McpStorage | None = None,
        event_store: McpEventStore | None = None,
    ) -> None:
        """Replace singletons — for tests only."""
        self._storage = storage
        self._event_store = event_store


_registry = _SingletonRegistry()


def get_mcp_storage() -> McpStorage:
    """Return the process-level McpStorage singleton (thread-safe)."""
    return _registry.get_storage()


def get_mcp_event_store() -> McpEventStore:
    """Return the process-level McpEventStore singleton (thread-safe)."""
    return _registry.get_event_store()


def _reset_singletons_for_testing(
    storage: McpStorage | None = None,
    event_store: McpEventStore | None = None,
) -> None:
    """Reset singletons for testing — replaces global instances."""
    _registry.reset(storage=storage, event_store=event_store)
