# l1 API Reference

> **Source**: `src/thegent/cache/l1.py`

L1 Memory Cache

In-memory TTL cache for fast access.

---

## CacheEntry

Cache entry with TTL.

### Methods

#### CacheEntry.is_expired

```python
is_expired(self: Any)
```

---

---

## L1MemoryCache

In-memory TTL cache.

### Methods

#### L1MemoryCache.__init__

```python
__init__(self: Any, ttl: float, max_size: int)
```

---

#### L1MemoryCache.clear

```python
clear(self: Any)
```

Clear all cache entries.

---

#### L1MemoryCache.delete

```python
delete(self: Any, key: str)
```

Delete value from cache.

---

#### L1MemoryCache.get

```python
get(self: Any, key: str)
```

Get value from cache.

---

#### L1MemoryCache.set

```python
set(self: Any, key: str, value: Any, ttl: Optional[float])
```

Set value in cache.

---

#### L1MemoryCache.stats

```python
stats(self: Any)
```

Get cache statistics.

---

---

## clear

```python
clear(self: Any)
```

Clear all cache entries.

---

## delete

```python
delete(self: Any, key: str)
```

Delete value from cache.

---

## get

```python
get(self: Any, key: str)
```

Get value from cache.

---

## is_expired

```python
is_expired(self: Any) -> bool
```

---

## set

```python
set(self: Any, key: str, value: Any, ttl: Optional[float])
```

Set value in cache.

---

## stats

```python
stats(self: Any)
```

Get cache statistics.

---

