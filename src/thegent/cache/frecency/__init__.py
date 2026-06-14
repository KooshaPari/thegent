"""Frecency cache for command, model, and resource history."""

from __future__ import annotations

import math
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from thegent.cache.multi_level import MultiLevelCache


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


@dataclass
class FrecencyEntry:
    """A frecency cache entry."""

    key: str
    score: float = 0.0
    access_count: int = 0
    last_access: datetime = field(default_factory=_utcnow)
    created: datetime = field(default_factory=_utcnow)

    def age_seconds(self, now: datetime | None = None) -> float:
        current = now or _utcnow()
        return max((current - self.last_access).total_seconds(), 0.0)

    def recalculate_score(self, half_life: float, now: datetime | None = None) -> float:
        lam = math.log(2) / half_life
        self.score = self.access_count * math.exp(-lam * self.age_seconds(now))
        return self.score

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["last_access"] = self.last_access.isoformat()
        payload["created"] = self.created.isoformat()
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> FrecencyEntry:
        return cls(
            key=str(payload["key"]),
            score=float(payload.get("score", 0.0)),
            access_count=int(payload.get("access_count", 0)),
            last_access=_coerce_datetime(payload.get("last_access", _utcnow())),
            created=_coerce_datetime(payload.get("created", _utcnow())),
        )


class FrecencyCache:
    """Frecency-based cache with optional MultiLevelCache persistence."""

    def __init__(
        self,
        maxsize: int = 256,
        half_life_seconds: float = 3600.0,
        storage: MultiLevelCache | None = None,
    ) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        if half_life_seconds <= 0:
            raise ValueError("half_life must be positive")
        self.maxsize = maxsize
        self.half_life = half_life_seconds
        self._storage = storage
        self._entries: dict[str, FrecencyEntry] = {}
        self._lock = threading.RLock()

    def access(self, key: str) -> float:
        with self._lock:
            entry = self._load_entry(key)
            if entry is None:
                if len(self._entries) >= self.maxsize:
                    self.evict_lowest(1)
                entry = FrecencyEntry(key=key)
                self._entries[key] = entry
            entry.access_count += 1
            entry.last_access = _utcnow()
            score = entry.recalculate_score(self.half_life, entry.last_access)
            self._persist_entry(entry)
            return score

    def score(self, key: str) -> float:
        with self._lock:
            entry = self._load_entry(key)
            if entry is None:
                return 0.0
            score = entry.recalculate_score(self.half_life)
            self._persist_entry(entry)
            return score

    def get_entry(self, key: str) -> FrecencyEntry | None:
        with self._lock:
            return self._load_entry(key)

    def top_n(self, n: int) -> list[FrecencyEntry]:
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return []
        with self._lock:
            for entry in self._entries.values():
                entry.recalculate_score(self.half_life)
            return sorted(self._entries.values(), key=lambda entry: entry.score, reverse=True)[:n]

    def evict_lowest(self, n: int) -> list[str]:
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return []
        with self._lock:
            for entry in self._entries.values():
                entry.recalculate_score(self.half_life)
            lowest = sorted(self._entries.values(), key=lambda entry: entry.score)[:n]
            evicted = [entry.key for entry in lowest]
            for key in evicted:
                self._entries.pop(key, None)
                self._delete_persisted(key)
            return evicted

    def clear(self) -> None:
        with self._lock:
            keys = list(self._entries)
            self._entries.clear()
            for key in keys:
                self._delete_persisted(key)

    def get(self, key: str) -> Any | None:
        entry = self.get_entry(key)
        return entry

    def set(self, key: str, value: Any) -> None:
        if isinstance(value, FrecencyEntry):
            with self._lock:
                self._entries[key] = value
                self._persist_entry(value)

    def update_score(self, key: str, delta: float) -> None:
        with self._lock:
            entry = self._load_entry(key)
            if entry is not None:
                entry.score += delta
                self._persist_entry(entry)

    def _load_entry(self, key: str) -> FrecencyEntry | None:
        entry = self._entries.get(key)
        if entry is not None:
            return entry
        if self._storage is None:
            return None
        payload = self._storage.get(self._storage_key(key))
        if payload is None:
            return None
        entry = FrecencyEntry.from_payload(payload)
        self._entries[key] = entry
        return entry

    def _persist_entry(self, entry: FrecencyEntry) -> None:
        if self._storage is not None:
            self._storage.set(self._storage_key(entry.key), entry.to_payload())

    def _delete_persisted(self, key: str) -> None:
        if self._storage is not None:
            self._storage.delete(self._storage_key(key))

    @staticmethod
    def _storage_key(key: str) -> str:
        return f"frecency:{key}"

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and self.get_entry(key) is not None


class FrecencyModelSelector:
    """Select models by observed frecency."""

    def __init__(
        self,
        *,
        maxsize: int = 256,
        half_life_seconds: float = 3600.0,
        storage: MultiLevelCache | None = None,
    ) -> None:
        self.cache = FrecencyCache(maxsize=maxsize, half_life_seconds=half_life_seconds, storage=storage)

    def record_use(self, model_id: str) -> float:
        return self.cache.access(model_id)

    def preferred_model(self, candidates: list[str]) -> str | None:
        if not candidates:
            return None
        return max(candidates, key=self.cache.score)

    def top_models(self, n: int) -> list[str]:
        return [entry.key for entry in self.cache.top_n(n)]

    def score(self, model_id: str) -> float:
        return self.cache.score(model_id)


__all__ = ["FrecencyCache", "FrecencyEntry", "FrecencyModelSelector", "_utcnow"]
