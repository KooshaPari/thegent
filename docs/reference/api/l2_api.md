# l2 API Reference

> **Source**: `src/thegent/cache/l2.py`

L2 Disk Cache

SQLite-backed disk cache for persistent storage.

---

## L2DiskCache

SQLite-backed disk cache.

### Methods

#### L2DiskCache.__init__

```python
__init__(self: Any, cache_dir: str, ttl: float)
```

---

#### L2DiskCache.clear

```python
clear(self: Any)
```

Clear all cache entries.

---

#### L2DiskCache.delete

```python
delete(self: Any, key: str)
```

Delete value from cache.

---

#### L2DiskCache.get

```python
get(self: Any, key: str)
```

Get value from cache.

---

#### L2DiskCache.set

```python
set(self: Any, key: str, value: Any, ttl: Optional[float])
```

Set value in cache.

---

#### L2DiskCache.stats

```python
stats(self: Any)
```

Get cache statistics.

---

---

## _DiskCacheModuleProtocol

Runtime import surface for the diskcache module.

---

## _DiskCacheProtocol

Minimal cache interface used by L2DiskCache.

### Methods

#### _DiskCacheProtocol.__init__

```python
__init__(self: Any, directory: str)
```

---

#### _DiskCacheProtocol.clear

```python
clear(self: Any)
```

---

#### _DiskCacheProtocol.delete

```python
delete(self: Any, key: str)
```

---

#### _DiskCacheProtocol.get

```python
get(self: Any, key: str, default: Any)
```

---

#### _DiskCacheProtocol.set

```python
set(self: Any, key: str, value: Any, expire: Any)
```

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

