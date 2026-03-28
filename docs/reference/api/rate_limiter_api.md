# rate_limiter API Reference

> **Source**: `src/thegent/utils/routing_impl/rate_limiter.py`

Sliding window rate limiter for LLM gateway use.

Prevents burst clustering at window resets unlike fixed-window counters
that allow 2x burst at boundary. Uses deque of timestamps per key with
per-key threading.Lock for thread safety.

No external dependencies — pure stdlib + dataclasses.

---

## MultiKeyRateLimiter

Rate limiter that enforces multiple limits simultaneously.

E.g., enforce both per-user AND per-provider limits on the same request.
All limits must pass for the request to be allowed.

### Methods

#### MultiKeyRateLimiter.__init__

```python
__init__(self: Any, limiter: Any)
```

---

#### MultiKeyRateLimiter.allow_all

```python
allow_all(self: Any, configs: list[RateLimitConfig])
```

Check all configs. Returns (all_allowed, results_list).

If any limit is exceeded, returns (False, results) without consuming
slots in limits that would have passed.

Atomic: either ALL slots are consumed or NONE are.

---

---

## RateLimitConfig

Configuration for a rate limit rule.

---

## RateLimitResult

Result of a rate limit check.

---

## SlidingWindowRateLimiter

Thread-safe sliding window rate limiter.

Uses a deque of timestamps per key. A request is allowed when
the count of timestamps within [now - window_seconds, now] < requests_per_window.
Evicts stale timestamps on every check.

Thread-safe via threading.Lock per key.

### Methods

#### SlidingWindowRateLimiter.__init__

```python
__init__(self: Any)
```

---

#### SlidingWindowRateLimiter.allow

```python
allow(self: Any, config: RateLimitConfig)
```

Check and consume a slot if allowed.

Returns RateLimitResult with allowed=True and consumes a slot,
or allowed=False without consuming.

---

#### SlidingWindowRateLimiter.check

```python
check(self: Any, config: RateLimitConfig)
```

Check if a request is allowed under the rate limit.

Does NOT consume a slot — use allow() for that.

---

#### SlidingWindowRateLimiter.get_current_count

```python
get_current_count(self: Any, key: str, window_seconds: float)
```

Return current request count within window for a key.

---

#### SlidingWindowRateLimiter.reset

```python
reset(self: Any, key: str)
```

Clear all timestamps for a key (e.g., after budget reset).

---

---

## allow

```python
allow(self: Any, config: RateLimitConfig)
```

Check and consume a slot if allowed.

Returns RateLimitResult with allowed=True and consumes a slot,
or allowed=False without consuming.

---

## allow_all

```python
allow_all(self: Any, configs: list[RateLimitConfig])
```

Check all configs. Returns (all_allowed, results_list).

If any limit is exceeded, returns (False, results) without consuming
slots in limits that would have passed.

Atomic: either ALL slots are consumed or NONE are.

---

## check

```python
check(self: Any, config: RateLimitConfig)
```

Check if a request is allowed under the rate limit.

Does NOT consume a slot — use allow() for that.

---

## get_current_count

```python
get_current_count(self: Any, key: str, window_seconds: float)
```

Return current request count within window for a key.

---

## get_rate_limiter

Get or create the module-level rate limiter singleton.

---

## make_provider_config

```python
make_provider_config(provider: str, requests_per_minute: int)
```

Convenience: build a per-provider per-minute rate limit config.

---

## make_user_config

```python
make_user_config(user_id: str, requests_per_minute: int)
```

Convenience: build a per-user per-minute rate limit config.

---

## reset

```python
reset(self: Any, key: str)
```

Clear all timestamps for a key (e.g., after budget reset).

---

