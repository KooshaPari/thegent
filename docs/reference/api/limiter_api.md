# limiter API Reference

> **Source**: `src/thegent/scaling/limiter.py`

Dynamic Limiter

Resource-based dynamic concurrency with hysteresis control.

---

## DynamicLimiter

Dynamic thread/concurrency limiter.

### Methods

#### DynamicLimiter.__init__

```python
__init__(self: Any, min_limit: int, max_limit: int, initial_limit: Optional[int], config: Optional[HysteresisConfig])
```

---

#### DynamicLimiter.acquire

```python
acquire(self: Any)
```

Try to acquire a slot.

---

#### DynamicLimiter.stats

```python
stats(self: Any)
```

Get limiter statistics.

---

---

## HysteresisConfig

Hysteresis controller configuration.

---

## acquire

```python
acquire(self: Any)
```

Try to acquire a slot.

---

## stats

```python
stats(self: Any)
```

Get limiter statistics.

---

