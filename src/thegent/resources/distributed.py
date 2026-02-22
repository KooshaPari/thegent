"""Distributed resource coordination backed by a file-locked JSON lease store.

Coordinates resource usage across multiple thegent nodes/processes using a
shared lease file at ``~/.thegent/resource_leases.json``.  A ``filelock``
advisory lock prevents concurrent writers from corrupting state; if
``filelock`` is not installed the module falls back to a simple read/write
approach that is safe for single-process use.
"""

from __future__ import annotations

import contextlib
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = [
    "DistributedResourceCoordinator",
    "ResourceCoordinationError",
    "ResourceLease",
]

# ---------------------------------------------------------------------------
# Optional filelock detection
# ---------------------------------------------------------------------------


def _has_filelock() -> bool:
    """Return True if the filelock package is importable."""
    try:
        import importlib.util

        return importlib.util.find_spec("filelock") is not None
    except Exception:
        return False


_FILELOCK_AVAILABLE: bool = _has_filelock()


class ResourceCoordinationError(Exception):
    """Raised when the coordinator cannot perform a lease operation."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ResourceLease:
    """A time-bounded claim on a portion of a named resource.

    Attributes:
        lease_id: Unique identifier for this lease.
        owner: Logical owner (agent id, process id, hostname, etc.).
        resource: Name of the resource being claimed.
        amount: Quantity of the resource reserved.
        expires_at: Unix timestamp after which the lease is considered expired.
    """

    lease_id: str
    owner: str
    resource: str
    amount: float
    expires_at: float

    @property
    def is_expired(self) -> bool:
        """Return True when the lease has passed its expiry time."""
        return time.time() >= self.expires_at

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ResourceLease:
        """Deserialise from a plain dictionary."""
        return cls(
            lease_id=str(data["lease_id"]),
            owner=str(data["owner"]),
            resource=str(data["resource"]),
            amount=float(data["amount"]),
            expires_at=float(data["expires_at"]),
        )


# ---------------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------------


class DistributedResourceCoordinator:
    """Coordinate resource usage across thegent nodes via a shared lease file.

    Uses ``filelock.FileLock`` for mutual exclusion when available, otherwise
    falls back to a simple read/write approach (safe for single-process use).

    Args:
        lease_file: Path to the JSON lease store.  Defaults to
            ``~/.thegent/resource_leases.json``.
        resource_limits: Optional mapping of ``resource -> total_capacity``.
            When provided, ``acquire`` enforces the limit automatically.
        lock_timeout: Seconds to wait for the file-lock before giving up.
    """

    _DEFAULT_LEASE_FILE = Path.home() / ".thegent" / "resource_leases.json"

    def __init__(
        self,
        lease_file: Path | None = None,
        resource_limits: dict | None = None,
        lock_timeout: float = 10.0,
    ) -> None:
        self._lease_file = Path(lease_file) if lease_file is not None else self._DEFAULT_LEASE_FILE
        self._resource_limits: dict = resource_limits or {}
        self._lock_timeout = lock_timeout
        self._lease_file.parent.mkdir(parents=True, exist_ok=True)

        if _FILELOCK_AVAILABLE:
            import filelock as fl

            self._filelock = fl.FileLock(str(self._lease_file) + ".lock", timeout=lock_timeout)
        else:
            self._filelock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(
        self,
        resource: str,
        amount: float,
        owner: str,
        ttl_s: float = 60.0,
        total: float | None = None,
    ) -> ResourceLease | None:
        """Acquire a lease on *amount* units of *resource*.

        Args:
            resource: Name of the resource to lease.
            amount: Quantity to reserve.
            owner: Identifier for the entity claiming the lease.
            ttl_s: Time-to-live in seconds before the lease automatically expires.
            total: Override total capacity for this call.  Falls back to
                ``resource_limits`` dict, then no limit (always succeeds).

        Returns:
            A :class:`ResourceLease` on success, or ``None`` if insufficient
            capacity is available.

        Raises:
            ResourceCoordinationError: If the lock cannot be acquired or
                storage I/O fails.
        """
        if amount <= 0:
            raise ResourceCoordinationError(f"amount must be positive, got {amount!r}")

        capacity = total if total is not None else self._resource_limits.get(resource)

        with self._locked():
            leases = self._read()
            self._purge_expired(leases)

            if capacity is not None:
                active_amount = sum(
                    lease.amount for lease in leases.values() if lease.resource == resource and not lease.is_expired
                )
                if active_amount + amount > capacity:
                    return None

            lease = ResourceLease(
                lease_id=str(uuid.uuid4()),
                owner=owner,
                resource=resource,
                amount=amount,
                expires_at=time.time() + ttl_s,
            )
            leases[lease.lease_id] = lease
            self._write(leases)
            return lease

    def release(self, lease_id: str) -> bool:
        """Release a lease by its identifier.

        Args:
            lease_id: The ``lease_id`` of the :class:`ResourceLease` to remove.

        Returns:
            ``True`` if the lease was found and removed, ``False`` otherwise.
        """
        with self._locked():
            leases = self._read()
            if lease_id not in leases:
                return False
            del leases[lease_id]
            self._write(leases)
            return True

    def get_active_leases(self, resource: str | None = None) -> list:
        """Return non-expired leases, optionally filtered by resource name.

        Args:
            resource: When given, only leases for this resource are returned.

        Returns:
            List of active :class:`ResourceLease` instances sorted by
            ``expires_at`` ascending.
        """
        with self._locked():
            leases = self._read()

        now = time.time()
        active = [
            lease
            for lease in leases.values()
            if lease.expires_at > now and (resource is None or lease.resource == resource)
        ]
        active.sort(key=lambda lease: lease.expires_at)
        return active

    def cleanup_expired(self) -> int:
        """Remove all expired leases from the store.

        Returns:
            Number of leases removed.
        """
        with self._locked():
            leases = self._read()
            before = len(leases)
            self._purge_expired(leases)
            after = len(leases)
            if before != after:
                self._write(leases)
            return before - after

    def get_available(self, resource: str, total: float) -> float:
        """Return available capacity for *resource* given a known *total*.

        Args:
            resource: Name of the resource.
            total: Known total capacity for the resource.

        Returns:
            ``total`` minus the sum of active (non-expired) lease amounts for
            *resource*.  Never returns a negative value.
        """
        active_amount = sum(lease.amount for lease in self.get_active_leases(resource=resource))
        return max(0.0, total - active_amount)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @contextlib.contextmanager
    def _locked(self) -> Generator[None, None, None]:
        """Context manager that acquires the file-lock when available."""
        if self._filelock is not None:
            with self._filelock:
                yield
        else:
            yield

    def _read(self) -> dict:
        """Read lease store from disk; returns empty dict if not yet created."""
        if not self._lease_file.exists():
            return {}
        try:
            raw = json.loads(self._lease_file.read_text(encoding="utf-8"))
            return {item["lease_id"]: ResourceLease.from_dict(item) for item in raw}
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise ResourceCoordinationError(f"Failed to parse lease store {self._lease_file}: {exc}") from exc

    def _write(self, leases: dict) -> None:
        """Persist lease store atomically (write-then-rename)."""
        payload = json.dumps(
            [lease.to_dict() for lease in leases.values()],
            indent=2,
        )
        tmp = self._lease_file.with_suffix(".tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(str(tmp), str(self._lease_file))
        except OSError as exc:
            raise ResourceCoordinationError(f"Failed to write lease store {self._lease_file}: {exc}") from exc

    @staticmethod
    def _purge_expired(leases: dict) -> None:
        """Remove expired leases in-place from a lease dict."""
        now = time.time()
        expired = [lid for lid, lease in leases.items() if lease.expires_at <= now]
        for lid in expired:
            del leases[lid]
