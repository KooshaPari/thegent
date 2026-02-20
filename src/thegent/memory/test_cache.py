"""Tests for L1/L2 cache implementation."""

import tempfile
import time

from .cache import L1Cache, L2Cache, LayeredCache


class TestL1Cache:
    """L1 cache tests."""

    def test_set_and_get(self):
        """Test basic set/get."""
        cache = L1Cache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_lru_eviction(self):
        """Test LRU eviction when full."""
        cache = L1Cache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key3, should evict key2 (least recently used)
        cache.set("key3", "value3")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = L1Cache(ttl_seconds=1)
        cache.set("key1", "value1")

        # Should be available immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_stats(self):
        """Test cache statistics."""
        cache = L1Cache()
        cache.set("key1", "value1")

        # Hit
        cache.get("key1")
        # Miss
        cache.get("key_missing")

        stats = cache.stats()
        assert stats["hit_count"] == 1
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == 50.0
        assert stats["size"] == 1

    def test_clear(self):
        """Test clearing cache."""
        cache = L1Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Check counts before clear
        cache.get("key1")  # Hit
        assert cache.hit_count == 1

        # Clear should reset both counts and data
        cache.clear()
        assert cache.hit_count == 0
        assert cache.miss_count == 0

        # Data should be gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None

        # After get() calls, miss_count will be 2
        assert cache.miss_count == 2


class TestL2Cache:
    """L2 cache tests."""

    def test_set_and_get(self):
        """Test basic file-based set/get."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L2Cache(cache_dir=tmpdir)
            cache.set("key1", {"data": "value1"})

            assert cache.get("key1") == {"data": "value1"}

    def test_persistence(self):
        """Test data persists across cache instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write with first instance
            cache1 = L2Cache(cache_dir=tmpdir)
            cache1.set("key1", {"persistent": True})

            # Read with second instance
            cache2 = L2Cache(cache_dir=tmpdir)
            assert cache2.get("key1") == {"persistent": True}

    def test_ttl_expiration(self):
        """Test L2 TTL expiration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L2Cache(cache_dir=tmpdir, ttl_seconds=1)
            cache.set("key1", "value1")

            # Should exist immediately
            assert cache.get("key1") == "value1"

            # Wait for expiration
            time.sleep(1.1)
            assert cache.get("key1") is None

    def test_stats(self):
        """Test L2 statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L2Cache(cache_dir=tmpdir)
            cache.set("key1", "value1")

            # Hit
            cache.get("key1")
            # Miss
            cache.get("missing")

            stats = cache.stats()
            assert stats["hit_count"] == 1
            assert stats["miss_count"] == 1
            assert stats["size"] == 1

    def test_clear(self):
        """Test clearing L2 cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L2Cache(cache_dir=tmpdir)
            cache.set("key1", "value1")
            cache.set("key2", "value2")

            cache.clear()
            assert cache.get("key1") is None
            assert cache.get("key2") is None


class TestLayeredCache:
    """Layered cache tests."""

    def test_l1_hit(self):
        """Test L1 hit returns immediately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LayeredCache(l2_dir=tmpdir)
            cache.set("key1", "value1")

            # Should hit in L1
            assert cache.get("key1") == "value1"
            assert cache.l1.hit_count == 1

    def test_l2_fallback(self):
        """Test L2 fallback when L1 misses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LayeredCache(l2_dir=tmpdir)
            cache.set("key1", "value1")

            # Clear L1 (resets counters)
            cache.l1.clear()

            # Should fall back to L2
            assert cache.get("key1") == "value1"
            # After L2 fallback, value is in L1 but hit_count is 0 (set doesn't count as hit)
            # The next get() will be a hit
            assert cache.get("key1") == "value1"
            assert cache.l1.hit_count == 1  # Now in L1 after fallback

    def test_l2_miss(self):
        """Test when both layers miss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LayeredCache(l2_dir=tmpdir)

            # Should return None when not in either layer
            assert cache.get("missing") is None

    def test_set_stores_both_layers(self):
        """Test set stores in both L1 and L2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LayeredCache(l2_dir=tmpdir)
            cache.set("key1", "value1")

            # Should be in both
            assert cache.l1.get("key1") == "value1"
            assert cache.l2.get("key1") == "value1"

    def test_clear_both_layers(self):
        """Test clear removes from both layers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LayeredCache(l2_dir=tmpdir)
            cache.set("key1", "value1")
            cache.set("key2", "value2")

            cache.clear()

            assert cache.l1.get("key1") is None
            assert cache.l2.get("key1") is None
            assert cache.get("key1") is None
            assert cache.get("key2") is None


class TestPerformance:
    """Performance benchmarks for cache operations."""

    def test_l1_sub_millisecond(self):
        """Test L1 operations are sub-millisecond."""
        cache = L1Cache()

        # Populate
        for i in range(100):
            cache.set(f"key{i}", f"value{i}")

        # Time gets
        start = time.time()
        for i in range(100):
            cache.get(f"key{i}")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        # Should be very fast (< 1ms for 100 operations)
        avg_per_op = elapsed / 100
        assert avg_per_op < 1.0, f"L1 avg per op: {avg_per_op}ms (target: <1ms)"

    def test_l2_sub_10ms(self):
        """Test L2 operations are sub-10ms per operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = L2Cache(cache_dir=tmpdir)

            # Populate
            for i in range(10):
                cache.set(f"key{i}", {"data": f"value{i}"})

            # Time gets
            start = time.time()
            for i in range(10):
                cache.get(f"key{i}")
            elapsed = (time.time() - start) * 1000  # Convert to ms

            # Should be reasonably fast
            avg_per_op = elapsed / 10
            assert avg_per_op < 10.0, f"L2 avg per op: {avg_per_op}ms (target: <10ms)"
