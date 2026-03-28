# rate_limit API Reference

> **Source**: `src/thegent/production/rate_limit.py`

Rate Limiter

Token bucket rate limiting.

---

## MultiRateLimiter

Rate limiter with multiple buckets.

### Methods

#### MultiRateLimiter.__init__

```python
__init__(self: Any)
```

---

#### MultiRateLimiter.acquire

```python
acquire(self: Any, key: str, tokens: int, wait: bool)
```

Acquire tokens for a key.

---

#### MultiRateLimiter.get

```python
get(self: Any, key: str, config: Optional[RateLimitConfig])
```

Get or create rate limiter for key.

---

#### MultiRateLimiter.stats

```python
stats(self: Any)
```

Get statistics for all limiters.

---

---

## RateLimitConfig

Rate limit configuration.

---

## RateLimiter

Token bucket rate limiter.

### Methods

#### RateLimiter.__init__

```python
__init__(self: Any, config: Optional[RateLimitConfig])
```

---

#### RateLimiter.acquire

```python
acquire(self: Any, tokens: int, wait: bool)
```

Try to acquire tokens.

---

#### RateLimiter.available

```python
available(self: Any)
```

Get available tokens.

---

#### RateLimiter.stats

```python
stats(self: Any)
```

Get rate limiter statistics.

---

#### RateLimiter.try_acquire

```python
try_acquire(self: Any, tokens: int)
```

Non-blocking acquire.

---

#### RateLimiter.wait_acquire

```python
wait_acquire(self: Any, tokens: int)
```

Blocking acquire with wait.

---

---

## acquire

```python
acquire(self: Any, key: str, tokens: int, wait: bool)
```

Acquire tokens for a key.

---

## available

```python
available(self: Any)
```

Get available tokens.

---

## get

```python
get(self: Any, key: str, config: Optional[RateLimitConfig])
```

Get or create rate limiter for key.

---

## stats

```python
stats(self: Any)
```

Get statistics for all limiters.

---

## try_acquire

```python
try_acquire(self: Any, tokens: int)
```

Non-blocking acquire.

---

## wait_acquire

```python
wait_acquire(self: Any, tokens: int)
```

Blocking acquire with wait.

---

