# cache_v2 API Reference

> **Source**: `src/thegent/infra/cache_v2.py`

Phase 9: Request Coalescing v2 implementation.

Includes Singleflight, inotify cache invalidation, heat-based LRU, and multi-tier cache.

---

## CacheInvalidator

inotify-based cache invalidation.

### Methods

#### CacheInvalidator.__init__

```python
__init__(self: Any, cache: Any)
```

---

#### CacheInvalidator.stop

```python
stop(self: Any)
```

---

#### CacheInvalidator.watch

```python
watch(self: Any, directory: Path)
```

---

---

## CacheV2

Async-friendly TTL cache used by newer infra modules.

### Methods

#### CacheV2.__init__

```python
__init__(self: Any, root: Path, namespace: str)
```

---

---

## CrossProcessSingleflight

Implementation of Singleflight pattern across processes using file locks.

### Methods

#### CrossProcessSingleflight.__init__

```python
__init__(self: Any, coordination_dir: Path)
```

---

#### CrossProcessSingleflight.do

```python
do(self: Any, key: str, func: Callable[(Any, Any)], ttl: int)
```

Execute func for key, coalescing concurrent calls across processes.

---

---

## Handler

**Inherits from**: `watchdog.events.FileSystemEventHandler`

### Methods

#### Handler.__init__

```python
__init__(self: Any, cache: Any)
```

---

#### Handler.on_modified

```python
on_modified(self: Any, event: Any)
```

---

---

## HeatBasedLRU

LRU cache with heat-based eviction (frequency + decay).

### Methods

#### HeatBasedLRU.__init__

```python
__init__(self: Any, capacity: int, decay_factor: float)
```

---

#### HeatBasedLRU.get

```python
get(self: Any, key: str)
```

---

#### HeatBasedLRU.put

```python
put(self: Any, key: str, value: Any)
```

---

---

## MultiTierCache

Multi-tier caching system with automatic tier management.

Tiers:
1. L1: cachetools TTLCache (fastest, automatic TTL, smallest)
2. L2: cachetools LRUCache (medium-term, configurable size)
3. L3: PersistDict (persistent, survives restarts, safe serialization)

### Methods

#### MultiTierCache.__init__

```python
__init__(self: Any, l1_size: int, l2_size: int, l3_path: Any, default_ttl: Any)
```

---

#### MultiTierCache.clear

```python
clear(self: Any)
```

---

#### MultiTierCache.delete

```python
delete(self: Any, key: str)
```

---

#### MultiTierCache.enable_invalidation

```python
enable_invalidation(self: Any, directory: Any)
```

Enable real-time cache invalidation based on file changes.

---

#### MultiTierCache.get

```python
get(self: Any, key: str)
```

---

#### MultiTierCache.get_with_fetch

```python
get_with_fetch(self: Any, key: str, fetch_func: Any, ttl: Any)
```

Get value from cache, or fetch and store if missing (Singleflight coalescing).

---

#### MultiTierCache.set

```python
set(self: Any, key: str, value: Any, ttl: Any)
```

---

#### MultiTierCache.stats

```python
stats(self: Any)
```

---

---

## Singleflight

Implementation of Singleflight pattern to prevent duplicate requests.

### Methods

#### Singleflight.__init__

```python
__init__(self: Any)
```

---

#### Singleflight.do

```python
do(self: Any, key: str, func: Callable[(Any, Any)])
```

Execute func for key, coalescing concurrent calls.

---

---

## clear

```python
clear(self: Any) -> None
```

---

## delete

```python
delete(self: Any, key: str) -> None
```

---

## do

```python
do(self: Any, key: str, func: Callable[(Any, Any)], ttl: int)
```

Execute func for key, coalescing concurrent calls across processes.

---

## enable_invalidation

```python
enable_invalidation(self: Any, directory: Any)
```

Enable real-time cache invalidation based on file changes.

---

## get

```python
get(self: Any, key: str) -> Any
```

---

## get_cache

```python
get_cache(l1_size: int, l2_size: int, l3_path: Any, default_ttl: Any)
```

Get global multi-tier cache instance.

---

## get_with_fetch

```python
get_with_fetch(self: Any, key: str, fetch_func: Any, ttl: Any)
```

Get value from cache, or fetch and store if missing (Singleflight coalescing).

---

## on_modified

```python
on_modified(self: Any, event: Any)
```

---

## put

```python
put(self: Any, key: str, value: Any)
```

---

## set

```python
set(self: Any, key: str, value: Any, ttl: Any) -> None
```

---

## stats

```python
stats(self: Any) -> dict[(str, Any)]
```

---

## stop

```python
stop(self: Any)
```

---

## watch

```python
watch(self: Any, directory: Path)
```

---

