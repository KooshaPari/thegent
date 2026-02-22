"""Connector field mapping cache with TTL support.

# @trace WL-191
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class MappingEntry:
    """Cached mapping entry for a connector field.

    Attributes:
        connector: Connector name (e.g., 'github', 'linear').
        field_id: Remote field identifier.
        field_name: Local field name.
        cached_at: Timestamp when the entry was cached (seconds since epoch).
        ttl_seconds: Time-to-live in seconds.
    """

    connector: str
    field_id: str
    field_name: str
    cached_at: float
    ttl_seconds: int


class ConnectorMappingCache:
    """Cache for connector field name → field_id mappings with TTL support."""

    DEFAULT_CACHE_FILE = Path("docs/reference/connector_mapping_cache.json")

    def __init__(self, cache_file: Optional[Path] = None) -> None:
        """Initialize the mapping cache.

        Args:
            cache_file: Path to cache JSON file. Defaults to
                       docs/reference/connector_mapping_cache.json.
        """
        self._cache_file = cache_file or self.DEFAULT_CACHE_FILE
        self._entries: dict[str, MappingEntry] = {}
        self._load()

    def _load(self) -> None:
        """Load cache from file if it exists."""
        if not self._cache_file.exists():
            return

        try:
            data = json.loads(self._cache_file.read_text(encoding="utf-8"))
            for key, entry_dict in data.items():
                entry = MappingEntry(
                    connector=entry_dict["connector"],
                    field_id=entry_dict["field_id"],
                    field_name=entry_dict["field_name"],
                    cached_at=entry_dict["cached_at"],
                    ttl_seconds=entry_dict["ttl_seconds"],
                )
                self._entries[key] = entry
        except (json.JSONDecodeError, KeyError):
            # If cache file is corrupt, start fresh
            self._entries = {}

    def _save(self) -> None:
        """Persist cache to file."""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        data = {k: asdict(v) for k, v in self._entries.items()}
        self._cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _make_key(self, connector: str, field_name: str) -> str:
        """Create a cache key from connector and field name."""
        return f"{connector}:{field_name}"

    def is_stale(self, entry: MappingEntry) -> bool:
        """Check if an entry has expired based on TTL.

        Args:
            entry: MappingEntry to check.

        Returns:
            True if the entry has expired, False otherwise.
        """
        current_time = time.time()
        elapsed = current_time - entry.cached_at
        return elapsed > entry.ttl_seconds

    def get(self, connector: str, field_name: str) -> Optional[str]:
        """Get cached field_id for a connector+field_name pair.

        Returns None if not cached, expired, or not found.

        Args:
            connector: Connector name.
            field_name: Field name to look up.

        Returns:
            Cached field_id or None.
        """
        key = self._make_key(connector, field_name)
        entry = self._entries.get(key)

        if entry is None:
            return None

        if self.is_stale(entry):
            del self._entries[key]
            self._save()
            return None

        return entry.field_id

    def put(self, connector: str, field_name: str, field_id: str, ttl_seconds: int = 3600) -> None:
        """Cache a connector field mapping.

        Args:
            connector: Connector name.
            field_name: Local field name.
            field_id: Remote field identifier.
            ttl_seconds: Time-to-live in seconds (default: 3600 = 1 hour).
        """
        key = self._make_key(connector, field_name)
        entry = MappingEntry(
            connector=connector,
            field_id=field_id,
            field_name=field_name,
            cached_at=time.time(),
            ttl_seconds=ttl_seconds,
        )
        self._entries[key] = entry
        self._save()

    def invalidate(self, connector: str, field_name: str) -> None:
        """Remove a cached entry.

        Args:
            connector: Connector name.
            field_name: Field name to invalidate.
        """
        key = self._make_key(connector, field_name)
        if key in self._entries:
            del self._entries[key]
            self._save()

    def clear_stale(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed.
        """
        stale_keys = [key for key, entry in self._entries.items() if self.is_stale(entry)]
        for key in stale_keys:
            del self._entries[key]

        if stale_keys:
            self._save()

        return len(stale_keys)
