"""Tests for thegent.integrations.connector_mapping_cache — Connector field mapping cache.

@trace WL-191
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from thegent.integrations.connector_mapping_cache import (
    ConnectorMappingCache,
    MappingEntry,
)


class TestMappingEntry:
    """Test MappingEntry dataclass. @trace WL-191"""

    @pytest.mark.requirement("WL-191")
    def test_create_entry(self) -> None:
        """Can create a MappingEntry with all fields."""
        current_time = time.time()
        entry = MappingEntry(
            connector="github",
            field_id="field_123",
            field_name="status",
            cached_at=current_time,
            ttl_seconds=3600,
        )

        assert entry.connector == "github"
        assert entry.field_id == "field_123"
        assert entry.field_name == "status"
        assert entry.cached_at == current_time
        assert entry.ttl_seconds == 3600


class TestConnectorMappingCache:
    """Test ConnectorMappingCache operations. @trace WL-191"""

    @pytest.fixture
    def cache(self, tmp_path: Path) -> ConnectorMappingCache:
        """Provide a ConnectorMappingCache with tmp cache file."""
        cache_file = tmp_path / "cache.json"
        return ConnectorMappingCache(cache_file=cache_file)

    @pytest.mark.requirement("WL-191")
    def test_cache_put_and_get(self, cache: ConnectorMappingCache) -> None:
        """Can store and retrieve a cached mapping."""
        cache.put("github", "status_field", "field_123", ttl_seconds=3600)
        result = cache.get("github", "status_field")

        assert result == "field_123"

    @pytest.mark.requirement("WL-191")
    def test_cache_get_missing(self, cache: ConnectorMappingCache) -> None:
        """get returns None for missing entries."""
        result = cache.get("github", "nonexistent")
        assert result is None

    @pytest.mark.requirement("WL-191")
    def test_cache_invalidate(self, cache: ConnectorMappingCache) -> None:
        """invalidate removes a cached entry."""
        cache.put("github", "status_field", "field_123")
        assert cache.get("github", "status_field") == "field_123"

        cache.invalidate("github", "status_field")
        assert cache.get("github", "status_field") is None

    @pytest.mark.requirement("WL-191")
    def test_cache_ttl_expiration(self, cache: ConnectorMappingCache) -> None:
        """Expired entries are returned as None."""
        # Put with very short TTL
        cache.put("github", "status_field", "field_123", ttl_seconds=0)

        # Entry should be immediately stale
        assert cache.get("github", "status_field") is None

    @pytest.mark.requirement("WL-191")
    def test_is_stale(self, cache: ConnectorMappingCache) -> None:
        """is_stale correctly identifies expired entries."""
        entry_fresh = MappingEntry(
            connector="github",
            field_id="field_123",
            field_name="status",
            cached_at=time.time(),
            ttl_seconds=3600,
        )

        entry_stale = MappingEntry(
            connector="github",
            field_id="field_456",
            field_name="priority",
            cached_at=time.time() - 7200,  # 2 hours ago
            ttl_seconds=3600,
        )

        assert not cache.is_stale(entry_fresh)
        assert cache.is_stale(entry_stale)

    @pytest.mark.requirement("WL-191")
    def test_clear_stale(self, cache: ConnectorMappingCache) -> None:
        """clear_stale removes only expired entries."""
        # Add one fresh and one stale
        cache.put("github", "fresh", "field_1", ttl_seconds=3600)

        # Manually add a stale entry to the cache
        stale_entry = MappingEntry(
            connector="github",
            field_id="field_2",
            field_name="stale",
            cached_at=time.time() - 7200,  # 2 hours ago
            ttl_seconds=3600,
        )
        cache._entries["github:stale"] = stale_entry

        # Clear stale
        removed_count = cache.clear_stale()

        assert removed_count == 1
        assert cache.get("github", "fresh") == "field_1"
        assert cache.get("github", "stale") is None

    @pytest.mark.requirement("WL-191")
    def test_cache_persistence(self, tmp_path: Path) -> None:
        """Cache is persisted to disk and reloaded."""
        cache_file = tmp_path / "cache.json"
        cache1 = ConnectorMappingCache(cache_file=cache_file)

        cache1.put("github", "status", "field_1", ttl_seconds=3600)
        cache1.put("linear", "priority", "field_2", ttl_seconds=3600)

        # Create new cache instance from same file
        cache2 = ConnectorMappingCache(cache_file=cache_file)

        assert cache2.get("github", "status") == "field_1"
        assert cache2.get("linear", "priority") == "field_2"

    @pytest.mark.requirement("WL-191")
    def test_cache_multiple_connectors(self, cache: ConnectorMappingCache) -> None:
        """Cache handles multiple connectors independently."""
        cache.put("github", "status", "gh_field_1")
        cache.put("linear", "status", "linear_field_1")

        assert cache.get("github", "status") == "gh_field_1"
        assert cache.get("linear", "status") == "linear_field_1"

        cache.invalidate("github", "status")
        assert cache.get("github", "status") is None
        assert cache.get("linear", "status") == "linear_field_1"
