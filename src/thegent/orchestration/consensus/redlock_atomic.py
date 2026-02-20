"""Redlock-based atomic distributed lock for swarm coordination.

Implements the Redlock algorithm (https://redis.io/docs/manual/patterns/distributed-locks/)
using SET NX PX across multiple Redis nodes with quorum consensus for
fault-tolerant distributed mutual exclusion.

Falls back to an in-process threading.Lock when Redis is not installed
or unreachable, with a logged warning.

Configuration via environment variable:
  THGENT_REDLOCK_NODES  - Comma-separated Redis URLs
                          (default: redis://localhost:6379)

swarm-redlock-atomic
"""

from __future__ import annotations

import contextlib
import importlib
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lua scripts for atomic Redis operations
# ---------------------------------------------------------------------------

# Delete key only if value matches lock_id (prevents accidental foreign release)
_RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

# Extend TTL only if value matches lock_id
_EXTEND_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("pexpire", KEYS[1], ARGV[2])
else
    return 0
end
"""

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RedlockAcquireResult:
    """Result returned from ``RedlockController.acquire``."""

    acquired: bool
    lock_id: str
    expires_at: float  # time.monotonic() value; 0.0 when acquired=False


# ---------------------------------------------------------------------------
# In-memory fallback lock
# ---------------------------------------------------------------------------


@dataclass
class _InMemoryLockState:
    """In-process lock state used when Redis is unavailable."""

    _lock: threading.Lock = field(default_factory=threading.Lock)
    _held_by: str | None = field(default=None)
    _expires_at: float = field(default=0.0)

    def _is_held(self) -> bool:
        """Return True if lock is currently held and not expired."""
        if self._held_by is None:
            return False
        if time.monotonic() >= self._expires_at:
            # Expired — auto-release
            self._held_by = None
            self._expires_at = 0.0
            return False
        return True

    def acquire(self, lock_id: str, ttl_ms: int) -> bool:
        """Acquire the in-memory lock. Returns True if successful."""
        with self._lock:
            if self._is_held():
                return False
            self._held_by = lock_id
            self._expires_at = time.monotonic() + ttl_ms / 1000.0
            return True

    def release(self, lock_id: str) -> bool:
        """Release the lock if held by lock_id. Returns True if released."""
        with self._lock:
            if self._held_by == lock_id and self._is_held():
                self._held_by = None
                self._expires_at = 0.0
                return True
            return False

    def extend(self, lock_id: str, ttl_ms: int) -> bool:
        """Extend TTL if still owned by lock_id. Returns True if extended."""
        with self._lock:
            if self._held_by == lock_id and self._is_held():
                self._expires_at = time.monotonic() + ttl_ms / 1000.0
                return True
            return False

    def is_locked(self) -> bool:
        """Return True if a valid lock is currently held."""
        with self._lock:
            return self._is_held()


# ---------------------------------------------------------------------------
# Redis client helpers
# ---------------------------------------------------------------------------


def _import_redis_sync() -> Any:
    """Import redis (sync); return module or None if not installed."""
    with contextlib.suppress(ImportError):
        return importlib.import_module("redis")
    return None


def _parse_redis_url(url: str) -> dict[str, Any]:
    """Parse a redis://[password@]host[:port][/db] URL into kwargs for redis.Redis."""
    rest = url
    for scheme in ("redis://", "rediss://"):
        if rest.startswith(scheme):
            rest = rest[len(scheme) :]
            break

    password: str | None = None
    if "@" in rest:
        creds, rest = rest.rsplit("@", 1)
        password = creds.lstrip(":")

    db = 0
    if "/" in rest:
        host_port, db_str = rest.split("/", 1)
        with contextlib.suppress(ValueError):
            db = int(db_str)
    else:
        host_port = rest

    host = "localhost"
    port = 6379
    if ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
        with contextlib.suppress(ValueError):
            port = int(port_str)
    elif host_port:
        host = host_port

    kwargs: dict[str, Any] = {
        "host": host,
        "port": port,
        "db": db,
        "decode_responses": True,
        "socket_connect_timeout": 2,
        "socket_timeout": 2,
    }
    if password:
        kwargs["password"] = password
    return kwargs


# ---------------------------------------------------------------------------
# Per-node operation helpers (keeps try-except out of loop bodies)
# ---------------------------------------------------------------------------


def _node_setnx(client: Any, key: str, lock_id: str, ttl_ms: int) -> int:
    """Attempt SET NX PX on one node; return 1 on success, 0 on failure."""
    try:
        ok = client.set(key, lock_id, nx=True, px=ttl_ms)
        return 1 if ok else 0
    except Exception as exc:
        _log.debug("redlock_atomic: node setnx failed: %s", exc)
        return 0


def _node_eval_release(client: Any, script: str, key: str, lock_id: str) -> int:
    """Run release Lua script on one node; return 1 if deleted, 0 otherwise."""
    try:
        result = client.eval(script, 1, key, lock_id)
        return 1 if result == 1 else 0
    except Exception as exc:
        _log.debug("redlock_atomic: node eval release failed: %s", exc)
        return 0


def _node_eval_extend(client: Any, script: str, key: str, lock_id: str, ttl_ms: int) -> int:
    """Run extend Lua script on one node; return 1 if extended, 0 otherwise."""
    try:
        result = client.eval(script, 1, key, lock_id, str(ttl_ms))
        return 1 if result == 1 else 0
    except Exception as exc:
        _log.debug("redlock_atomic: node eval extend failed: %s", exc)
        return 0


def _node_exists(client: Any, key: str) -> bool:
    """Check if key exists on one node; return False on error."""
    try:
        return bool(client.exists(key))
    except Exception as exc:
        _log.debug("redlock_atomic: node exists failed: %s", exc)
        return False


def _node_eval_silent(client: Any, script: str, key: str, lock_id: str) -> None:
    """Run Lua script on one node, ignoring any errors (best-effort)."""
    with contextlib.suppress(Exception):
        client.eval(script, 1, key, lock_id)


def _new_lock_id() -> str:
    """Generate a unique lock identifier."""
    return uuid.uuid4().hex


def _parse_node_urls_from_env() -> list[str]:
    """Read redlock nodes from settings and return list of Redis URLs."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    raw = settings.redlock_nodes
    return [u.strip() for u in raw.split(",") if u.strip()]


# ---------------------------------------------------------------------------
# RedlockController
# ---------------------------------------------------------------------------


class RedlockController:
    """Distributed Redlock-style acquire/release for a single named key.

    When multiple Redis nodes are configured (``THGENT_REDLOCK_NODES``), uses
    quorum consensus: a lock is acquired when SET NX PX succeeds on a majority
    (> N/2) of nodes and the total time taken is less than the requested TTL.

    When only one node is configured (the common case), degrades gracefully to
    a simple ``SET key lock_id NX PX ttl`` on that single node.

    On Redis unavailability (import error *or* connection error), falls back to
    an in-process ``threading.Lock`` with a warning log — suitable for
    single-process usage.
    """

    def __init__(
        self,
        key: str,
        ttl_ms: int = 5000,
        *,
        redis_nodes: list[str] | None = None,
    ) -> None:
        """Create a controller for the given lock key.

        Args:
            key: The Redis key name for the lock.
            ttl_ms: Lock TTL in milliseconds.  Stale locks auto-expire.
            redis_nodes: List of Redis URLs.  When ``None``, reads
                         ``THGENT_REDLOCK_NODES`` from the environment,
                         defaulting to ``["redis://localhost:6379"]``.
        """
        self._key = key
        self._ttl_ms = ttl_ms
        self._nodes_urls: list[str] = redis_nodes if redis_nodes is not None else _parse_node_urls_from_env()
        self._clients: list[Any] = []
        self._fallback: _InMemoryLockState | None = None
        self._redis_available = False

        self._try_connect_nodes()

    # ------------------------------------------------------------------
    # Connection setup
    # ------------------------------------------------------------------

    def _try_connect_nodes(self) -> None:
        """Attempt to build Redis clients for all configured nodes."""
        redis_mod = _import_redis_sync()
        if redis_mod is None:
            _log.warning(
                "redlock_atomic: redis package not installed; falling back to in-process lock for key=%r",
                self._key,
            )
            self._fallback = _InMemoryLockState()
            return

        clients = []
        for url in self._nodes_urls:
            kwargs = _parse_redis_url(url)
            try:
                client = redis_mod.Redis(**kwargs)
                # Probe connectivity
                client.ping()
                clients.append(client)
            except Exception as exc:
                _log.warning("redlock_atomic: cannot connect to node %r: %s", url, exc)

        if not clients:
            _log.warning(
                "redlock_atomic: no Redis nodes reachable; falling back to in-process lock for key=%r",
                self._key,
            )
            self._fallback = _InMemoryLockState()
            return

        self._clients = clients
        self._redis_available = True
        _log.debug(
            "redlock_atomic: connected to %d/%d Redis node(s) for key=%r",
            len(clients),
            len(self._nodes_urls),
            self._key,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self) -> RedlockAcquireResult:
        """Attempt to acquire the distributed lock atomically.

        Uses ``SET key lock_id NX PX ttl`` on each configured Redis node.
        For multi-node setups, requires quorum (majority) and validates that
        the elapsed time is within the granted TTL (drift-aware check).

        Returns:
            ``RedlockAcquireResult`` with ``acquired=True`` and a unique
            ``lock_id`` on success; ``acquired=False, lock_id="", expires_at=0.0``
            on failure.
        """
        if self._fallback is not None:
            return self._acquire_fallback()
        return self._acquire_redis()

    def release(self, lock_id: str) -> bool:
        """Release the lock atomically only if we are the owner.

        Uses a Lua script (``GET`` + ``DEL``) to ensure we never delete a lock
        held by another process/thread.

        Args:
            lock_id: The token returned by a successful ``acquire()`` call.

        Returns:
            ``True`` if the lock was released; ``False`` if not held or
            already expired.
        """
        if self._fallback is not None:
            return self._fallback.release(lock_id)
        return self._release_redis(lock_id)

    def extend(self, lock_id: str, ttl_ms: int) -> bool:
        """Extend the lock TTL if still owned.

        Uses a Lua script to atomically extend only when the lock is still held
        by the given ``lock_id``.

        Args:
            lock_id: The token from the original ``acquire()`` call.
            ttl_ms: New TTL in milliseconds from now.

        Returns:
            ``True`` if the TTL was extended; ``False`` otherwise.
        """
        if self._fallback is not None:
            return self._fallback.extend(lock_id, ttl_ms)
        return self._extend_redis(lock_id, ttl_ms)

    def is_locked(self) -> bool:
        """Return ``True`` if any valid lock exists for this key.

        Note: This is a point-in-time check subject to race conditions; do not
        use it for coordination decisions — use ``acquire()`` instead.
        """
        if self._fallback is not None:
            return self._fallback.is_locked()
        return self._is_locked_redis()

    def is_available(self) -> bool:
        """Return ``True`` when backed by real Redis (not in-memory fallback)."""
        return self._redis_available

    # ------------------------------------------------------------------
    # Redis implementation
    # ------------------------------------------------------------------

    def _acquire_redis(self) -> RedlockAcquireResult:
        """Redlock acquire across all configured nodes."""
        lock_id = _new_lock_id()
        start = time.monotonic()
        quorum = len(self._clients) // 2 + 1
        acquired_count = sum(_node_setnx(client, self._key, lock_id, self._ttl_ms) for client in self._clients)

        elapsed_ms = (time.monotonic() - start) * 1000
        validity_ms = self._ttl_ms - elapsed_ms

        if acquired_count >= quorum and validity_ms > 0:
            expires_at = time.monotonic() + validity_ms / 1000.0
            _log.debug(
                "redlock_atomic: acquired key=%r lock_id=%s quorum=%d/%d validity=%.1fms",
                self._key,
                lock_id,
                acquired_count,
                len(self._clients),
                validity_ms,
            )
            return RedlockAcquireResult(acquired=True, lock_id=lock_id, expires_at=expires_at)

        # Failed to reach quorum — release any partial locks we set
        self._release_partial(lock_id)
        _log.debug(
            "redlock_atomic: acquire failed key=%r quorum=%d/%d needed=%d",
            self._key,
            acquired_count,
            len(self._clients),
            quorum,
        )
        return RedlockAcquireResult(acquired=False, lock_id="", expires_at=0.0)

    def _release_redis(self, lock_id: str) -> bool:
        """Release lock on all nodes; return True if at least one released."""
        released = sum(_node_eval_release(client, _RELEASE_SCRIPT, self._key, lock_id) for client in self._clients)
        released_ok = released > 0
        _log.debug(
            "redlock_atomic: release key=%r lock_id=%s released=%d/%d",
            self._key,
            lock_id,
            released,
            len(self._clients),
        )
        return released_ok

    def _extend_redis(self, lock_id: str, ttl_ms: int) -> bool:
        """Extend TTL on all nodes; return True if quorum extended."""
        quorum = len(self._clients) // 2 + 1
        extended = sum(
            _node_eval_extend(client, _EXTEND_SCRIPT, self._key, lock_id, ttl_ms) for client in self._clients
        )
        extended_ok = extended >= quorum
        _log.debug(
            "redlock_atomic: extend key=%r lock_id=%s extended=%d/%d ok=%s",
            self._key,
            lock_id,
            extended,
            len(self._clients),
            extended_ok,
        )
        return extended_ok

    def _is_locked_redis(self) -> bool:
        """Check if key exists on at least one node."""
        return any(_node_exists(client, self._key) for client in self._clients)

    def _release_partial(self, lock_id: str) -> None:
        """Best-effort release after failed quorum acquire."""
        for client in self._clients:
            _node_eval_silent(client, _RELEASE_SCRIPT, self._key, lock_id)

    # ------------------------------------------------------------------
    # Fallback (in-memory) implementation
    # ------------------------------------------------------------------

    def _acquire_fallback(self) -> RedlockAcquireResult:
        assert self._fallback is not None
        lock_id = _new_lock_id()
        if self._fallback.acquire(lock_id, self._ttl_ms):
            expires_at = time.monotonic() + self._ttl_ms / 1000.0
            return RedlockAcquireResult(acquired=True, lock_id=lock_id, expires_at=expires_at)
        return RedlockAcquireResult(acquired=False, lock_id="", expires_at=0.0)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def make_redlock_controller(key: str, **kwargs: Any) -> RedlockController:
    """Create a ``RedlockController`` for the given lock key.

    Keyword arguments are forwarded to ``RedlockController.__init__``
    (e.g. ``ttl_ms``, ``redis_nodes``).

    Example::

        rl = make_redlock_controller("my-lock", ttl_ms=3000)
        result = rl.acquire()
        if result.acquired:
            try:
                ...
            finally:
                rl.release(result.lock_id)
    """
    return RedlockController(key, **kwargs)
