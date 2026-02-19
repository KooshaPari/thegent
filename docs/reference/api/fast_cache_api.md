# fast_cache API Reference

> **Source**: `src/thegent/infra/fast_cache.py`

Multi-tier caching system for optimal performance.

This module provides a high-performance multi-tier caching system:
- L1: cachetools TTLCache (fastest, automatic TTL, smallest)
- L2: cachetools LRUCache (medium-term, configurable size)
- L3: diskcache (persistent, survives restarts)

Performance improvements:
- Multi-tier caching reduces memory pressure
- Persistent caching survives restarts
- Automatic tier promotion/demotion
- Configurable TTL and size limits
- Library-first (LIBRARY_FIRST_POLICY.md): Uses cachetools for all in-memory caching

---

## MultiTierCache

Multi-tier caching system with automatic tier management.

Tiers:
1. L1: In-memory dict (fastest, smallest, volatile)
2. L2: cachetools LRUCache (medium-term, configurable size)
3. L3: diskcache (persistent, survives restarts)

### Methods

#### MultiTierCache.__init__

Initialize multi-tier cache.

Args:
    l1_size: Maximum items in L1 cache
    l2_size: Maximum items in L2 cache
    l3_path: Path for L3 disk cache (None to disable)
    default_ttl: Default time-to-live in seconds (None = no expiry)

```python
__init__(self, l1_size, l2_size, l3_path, default_ttl)
```

#### MultiTierCache.clear

Clear all tiers.

```python
clear(self)
```

#### MultiTierCache.delete

Delete key from all tiers.

```python
delete(self, key)
```

#### MultiTierCache.get

Get value from cache (checks all tiers).

Args:
    key: Cache key

Returns:
    Cached value or None if not found

```python
get(self, key)
```

#### MultiTierCache.set

Set value in cache (stores in all tiers).

Args:
    key: Cache key
    value: Value to cache
    ttl: Time-to-live in seconds (uses default_ttl if None)

```python
set(self, key, value, ttl)
```

#### MultiTierCache.stats

Get cache statistics.

```python
stats(self)
```

---

## clear

Clear all tiers.

```python
clear(self)
```

---

## delete

Delete key from all tiers.

```python
delete(self, key)
```

---

## get

Get value from cache (checks all tiers).

Args:
    key: Cache key

Returns:
    Cached value or None if not found

```python
get(self, key)
```

---

## get_cache

Get global multi-tier cache instance.

Args:
    l1_size: Maximum items in L1 cache
    l2_size: Maximum items in L2 cache
    l3_path: Path for L3 disk cache
    default_ttl: Default time-to-live in seconds

Returns:
    MultiTierCache instance

```python
get_cache(l1_size, l2_size, l3_path, default_ttl)
```

---

## set

Set value in cache (stores in all tiers).

Args:
    key: Cache key
    value: Value to cache
    ttl: Time-to-live in seconds (uses default_ttl if None)

```python
set(self, key, value, ttl)
```

---

## stats

Get cache statistics.

```python
stats(self)
```

---

