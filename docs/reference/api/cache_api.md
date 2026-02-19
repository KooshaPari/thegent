# cache API Reference

> **Source**: `src/thegent/tools/cache.py`

## ResourceCache

WP-DX-023: Simple ETag-based caching for FastMCP resources.

Hybrid caching strategy:
- In-memory: TTLCache for fast access (cachetools handles TTL automatically)
- File-based: Persistent storage across sessions (manual JSON file I/O)
- ETag: Change detection for cache invalidation

### Methods

#### ResourceCache.__init__

```python
__init__(self, cache_dir, ttl_seconds, max_memory_items)
```

#### ResourceCache.clear

Clear both in-memory and file-based cache.

```python
clear(self)
```

#### ResourceCache.get

```python
get(self, key)
```

#### ResourceCache.set

```python
set(self, key, payload)
```

---

## clear

Clear both in-memory and file-based cache.

```python
clear(self)
```

---

## get

```python
get(self, key)
```

---

## set

```python
set(self, key, payload)
```

---

