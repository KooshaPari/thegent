"""Frecency-ranked cache: combines frequency + recency scoring.

Frecency = frequency × recency, where recency decays exponentially over time.

Formula:
    score = access_count × e^(-λ × age_seconds)
    λ     = ln(2) / half_life_seconds

A ``half_life_seconds`` of 3600 (1 hour) means an item's *recency* component
halves every hour regardless of access count.

Optionally persists frecency data via a :class:`~thegent.cache.MultiLevelCache`
L2 backend so scores survive process restarts.

FR traceability: FR-CACHE-002 (frecency algorithm for command/model/resource history)
"""

from __future__ import annotations

import contextlib
import math
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from thegent.cache.multi_level import MultiLevelCache

# Persistence key prefix stored in MultiLevelCache
_FRECENCY_PREFIX = "frecency:"


def _utcnow() -> datetime:
    """Return current UTC datetime (extracted for testability)."""
    return datetime.now(timezone.utc)


@dataclass
class FrecencyEntry:
    """Snapshot of frecency data for a single key.

    Attributes:
        key:          The tracked item key (e.g. model name, command name).
        score:        Current frecency score (frequency × recency decay).
        access_count: Total number of recorded accesses.
        last_access:  UTC timestamp of the most recent access.
        created:      UTC timestamp when the entry was first created.
    """

    key: str
    score: float
    access_count: int
    last_access: datetime
    created: datetime = field(default_factory=_utcnow)

    def age_seconds(self, now: datetime | None = None) -> float:
        """Return elapsed seconds since ``last_access``."""
        ref = now if now is not None else _utcnow()
        delta = ref - self.last_access
        return max(0.0, delta.total_seconds())

    def recalculate_score(self, half_life: float, now: datetime | None = None) -> float:
        """Recompute frecency score using the exponential decay formula.

        Args:
            half_life: Half-life in seconds for the recency decay factor.
            now:       Reference time (defaults to current UTC time).

        Returns:
            Updated score.  The entry's ``score`` attribute is mutated in place.
        """
        lam = math.log(2) / half_life
        age = self.age_seconds(now)
        self.score = self.access_count * math.exp(-lam * age)
        return self.score


class FrecencyCache:
    """Frecency-ranked in-memory cache with optional persistence.

    Args:
        maxsize:            Maximum number of entries held in memory.  When the
                            limit is exceeded, the lowest-scored entry is evicted.
        half_life_seconds:  Half-life for the exponential decay component.
                            Defaults to 3600 (1 hour).
        storage:            Optional :class:`~thegent.cache.MultiLevelCache`
                            instance for persisting frecency data across
                            process restarts.  When provided, entries are
                            loaded from storage on first access and written
                            back on every ``access()`` call.
    """

    def __init__(
        self,
        maxsize: int = 1000,
        half_life_seconds: float = 3600.0,
        storage: MultiLevelCache | None = None,
    ) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        if half_life_seconds <= 0:
            raise ValueError("half_life_seconds must be positive")

        self._maxsize = maxsize
        self._half_life = half_life_seconds
        self._storage = storage
        self._entries: dict[str, FrecencyEntry] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def access(self, key: str) -> float:
        """Record an access for *key* and return the updated frecency score.

        On first access, a new entry is created with ``access_count = 1``.
        On subsequent accesses, ``access_count`` is incremented, ``last_access``
        is refreshed, and the score is recomputed.

        If a ``storage`` backend was provided, the updated entry is persisted.

        If the cache is at ``maxsize`` capacity after inserting a new key, the
        lowest-scored entry is evicted to maintain the size bound.

        Args:
            key: Identifier for the accessed item.

        Returns:
            The new frecency score for *key*.
        """
        now = _utcnow()
        with self._lock:
            entry = self._entries.get(key)

            if entry is None:
                # Try to restore from persistent storage before creating fresh
                entry = self._load_from_storage(key)
                if entry is None:
                    entry = FrecencyEntry(
                        key=key,
                        score=0.0,
                        access_count=0,
                        last_access=now,
                        created=now,
                    )
                # Evict if at capacity before inserting
                if len(self._entries) >= self._maxsize:
                    self._evict_one()
                self._entries[key] = entry

            entry.access_count += 1
            entry.last_access = now
            score = entry.recalculate_score(self._half_life, now)

            self._persist_entry(entry)
            return score

    def score(self, key: str) -> float:
        """Return the current frecency score for *key* without recording an access.

        The score is recomputed using current wall-clock time so it reflects
        elapsed decay even without new accesses.

        Returns:
            Current score, or ``0.0`` if the key is unknown.
        """
        now = _utcnow()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                entry = self._load_from_storage(key)
                if entry is None:
                    return 0.0
                self._entries[key] = entry
            return entry.recalculate_score(self._half_life, now)

    def top_n(self, n: int) -> list[FrecencyEntry]:
        """Return the *n* highest-scoring entries, sorted descending.

        Scores are recomputed at call time to account for decay since last
        access.

        Args:
            n: Number of entries to return.  If *n* exceeds the number of
               tracked entries, all entries are returned.

        Returns:
            List of :class:`FrecencyEntry` sorted by score descending.
        """
        if n < 0:
            raise ValueError("n must be >= 0")
        now = _utcnow()
        with self._lock:
            for entry in self._entries.values():
                entry.recalculate_score(self._half_life, now)
            ranked = sorted(self._entries.values(), key=lambda e: e.score, reverse=True)
            return ranked[:n]

    def get_entry(self, key: str) -> FrecencyEntry | None:
        """Return the :class:`FrecencyEntry` for *key*, or ``None`` if absent.

        The entry's score is recomputed before it is returned.
        """
        now = _utcnow()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                entry = self._load_from_storage(key)
                if entry is None:
                    return None
                self._entries[key] = entry
            entry.recalculate_score(self._half_life, now)
            return entry

    def evict_lowest(self, n: int = 1) -> list[str]:
        """Evict the *n* lowest-scored entries and return their keys.

        Args:
            n: Number of entries to evict.  Clamped to the current entry count.

        Returns:
            List of evicted keys.
        """
        if n < 0:
            raise ValueError("n must be >= 0")
        now = _utcnow()
        with self._lock:
            for entry in self._entries.values():
                entry.recalculate_score(self._half_life, now)
            sorted_keys = sorted(self._entries, key=lambda k: self._entries[k].score)
            to_evict = sorted_keys[: min(n, len(sorted_keys))]
            for key in to_evict:
                del self._entries[key]
                self._delete_from_storage(key)
            return to_evict

    def clear(self) -> None:
        """Remove all entries from memory and (if configured) from storage."""
        with self._lock:
            keys = list(self._entries.keys())
            self._entries.clear()
            for key in keys:
                self._delete_from_storage(key)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def maxsize(self) -> int:
        """Maximum number of entries held in memory."""
        return self._maxsize

    @property
    def half_life(self) -> float:
        """Half-life in seconds for the exponential decay component."""
        return self._half_life

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def __contains__(self, key: object) -> bool:
        with self._lock:
            return key in self._entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_one(self) -> None:
        """Evict the single lowest-scored entry (must hold _lock)."""
        if not self._entries:
            return
        lowest = min(self._entries, key=lambda k: self._entries[k].score)
        del self._entries[lowest]
        self._delete_from_storage(lowest)

    def _storage_key(self, key: str) -> str:
        return f"{_FRECENCY_PREFIX}{key}"

    def _persist_entry(self, entry: FrecencyEntry) -> None:
        """Write *entry* to storage if a backend is configured (must hold _lock)."""
        if self._storage is None:
            return
        payload: dict[str, Any] = {
            "key": entry.key,
            "score": entry.score,
            "access_count": entry.access_count,
            "last_access": entry.last_access.isoformat(),
            "created": entry.created.isoformat(),
        }
        with contextlib.suppress(Exception):
            self._storage.set(self._storage_key(entry.key), payload)

    def _load_from_storage(self, key: str) -> FrecencyEntry | None:
        """Load a persisted entry from storage (must hold _lock).

        Returns None if storage is absent or the key is not found.
        """
        if self._storage is None:
            return None
        with contextlib.suppress(Exception):
            payload = self._storage.get(self._storage_key(key))
            if payload is None:
                return None
            return FrecencyEntry(
                key=payload["key"],
                score=float(payload["score"]),
                access_count=int(payload["access_count"]),
                last_access=datetime.fromisoformat(payload["last_access"]),
                created=datetime.fromisoformat(payload["created"]),
            )
        return None

    def _delete_from_storage(self, key: str) -> None:
        """Remove a persisted entry from storage (must hold _lock)."""
        if self._storage is None:
            return
        with contextlib.suppress(Exception):
            self._storage.delete(self._storage_key(key))


# ---------------------------------------------------------------------------
# FrecencyModelSelector
# ---------------------------------------------------------------------------


class FrecencyModelSelector:
    """Prefer recently-and-frequently used models using frecency scoring.

    Wraps a :class:`FrecencyCache` and exposes model-selection helpers.

    Example usage::

        selector = FrecencyModelSelector()
        selector.record_use("claude-sonnet-4-5")
        selector.record_use("claude-sonnet-4-5")
        selector.record_use("gemini-3-flash")

        best = selector.preferred_model(["claude-sonnet-4-5", "gemini-3-flash"])
        # -> "claude-sonnet-4-5"  (higher frecency)

    Args:
        maxsize:           Maximum number of models tracked.
        half_life_seconds: Recency half-life (default 3600 s = 1 hour).
        storage:           Optional persistence backend.
    """

    def __init__(
        self,
        maxsize: int = 100,
        half_life_seconds: float = 3600.0,
        storage: MultiLevelCache | None = None,
    ) -> None:
        self._cache = FrecencyCache(
            maxsize=maxsize,
            half_life_seconds=half_life_seconds,
            storage=storage,
        )

    def record_use(self, model_id: str) -> float:
        """Record that *model_id* was used.  Returns the updated score."""
        return self._cache.access(model_id)

    def preferred_model(self, candidates: list[str]) -> str | None:
        """Return the highest-scoring model from *candidates*.

        If none of the candidates have been recorded yet (all score 0), the
        first candidate is returned as a tiebreaker.

        Returns:
            The model identifier with the highest frecency score, or ``None``
            if *candidates* is empty.
        """
        if not candidates:
            return None
        return max(candidates, key=self._cache.score)

    def top_models(self, n: int) -> list[str]:
        """Return the *n* most frecently used model identifiers."""
        return [e.key for e in self._cache.top_n(n)]

    def score(self, model_id: str) -> float:
        """Return the current frecency score for *model_id*."""
        return self._cache.score(model_id)

    @property
    def cache(self) -> FrecencyCache:
        """Underlying :class:`FrecencyCache` for advanced access."""
        return self._cache
