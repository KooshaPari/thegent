"""Resource caching utilities for thegent."""

from __future__ import annotations

import hashlib
import orjson as json
import time
from pathlib import Path
from typing import Any


class ResourceCache:
    """Simple file-based resource cache with TTL support."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 300) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.json"

    def set(self, key: str, value: Any) -> str:
        """Store a value in the cache. Returns an etag (sha256 of content)."""
        payload = json.dumps(value, sort_keys=True).decode()
        etag = hashlib.sha256(payload.encode()).hexdigest()
        entry = {"value": value, "etag": etag, "stored_at": time.time()}
        self._key_path(key).write_text(json.dumps(entry).decode(), encoding="utf-8")
        return etag

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache. Returns None if expired or missing."""
        path = self._key_path(key)
        if not path.exists():
            return None
        entry = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - entry["stored_at"] > self.ttl_seconds:
            path.unlink(missing_ok=True)
            return None
        return entry["value"]
