# tiered API Reference

> **Source**: `src/thegent/cache/tiered.py`

Tiered Cache

Combines multiple cache layers with fallback.

---

## TieredCache

Multi-tier cache with L1 and L2 fallbacks.

### Methods

#### TieredCache.__init__

```python
__init__(self: Any, l1_ttl: float, l2_ttl: float, l1_max_size: int, l2_cache_dir: str)
```

---

#### TieredCache.clear

```python
clear(self: Any)
```

Clear all tiers.

---

#### TieredCache.delete

```python
delete(self: Any, key: str)
```

Delete from all tiers.

---

#### TieredCache.get

```python
get(self: Any, key: str)
```

Get from L1, fallback to L2.

---

#### TieredCache.get_or_set

```python
get_or_set(self: Any, key: str, factory: Callable[(Any, Any)], l1_ttl: Optional[float], l2_ttl: Optional[float])
```

Get from cache or compute and cache.

---

#### TieredCache.set

```python
set(self: Any, key: str, value: Any, l1_ttl: Optional[float], l2_ttl: Optional[float])
```

Set in both L1 and L2.

---

#### TieredCache.stats

```python
stats(self: Any)
```

Get combined statistics.

---

---

## clear

```python
clear(self: Any)
```

Clear all tiers.

---

## delete

```python
delete(self: Any, key: str)
```

Delete from all tiers.

---

## get

```python
get(self: Any, key: str)
```

Get from L1, fallback to L2.

---

## get_or_set

```python
get_or_set(self: Any, key: str, factory: Callable[(Any, Any)], l1_ttl: Optional[float], l2_ttl: Optional[float])
```

Get from cache or compute and cache.

---

## set

```python
set(self: Any, key: str, value: Any, l1_ttl: Optional[float], l2_ttl: Optional[float])
```

Set in both L1 and L2.

---

## stats

```python
stats(self: Any)
```

Get combined statistics.

---

