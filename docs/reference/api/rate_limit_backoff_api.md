# rate_limit_backoff API Reference

> **Source**: `src/thegent/integrations/rate_limit_backoff.py`

API Rate-Limit Backoff Controls (WL-169): Exponential backoff for rate-limited APIs.

Provides retry and backoff configuration for APIs that return 429 (Too Many Requests)
or 503 (Service Unavailable) responses. Uses tenacity for retry logic with
exponential backoff and jitter to avoid thundering herd.

The RateLimitBackoffManager can be used standalone for computing backoff times,
or integrated with tenacity decorators for automatic retry.

---

## RateLimitBackoffManager

Manager for rate-limit backoff and retry configuration.

### Methods

#### RateLimitBackoffManager.__init__

```python
__init__(self: Any, config: Any)
```

Initialize the rate-limit manager.

**Parameters**:

- `config`: Rate-limit configuration. Defaults to RateLimitConfig().

---

#### RateLimitBackoffManager.compute_wait

```python
compute_wait(self: Any, attempt: int)
```

Compute wait time for a given attempt number.

Uses exponential backoff with jitter:
    wait = min(initial_wait * (multiplier ** attempt) + random_jitter, max_wait)

**Parameters**:

- `attempt`: The attempt number (0-indexed, so first retry is attempt=1).

**Returns**: Wait time in seconds.

---

#### RateLimitBackoffManager.get_retry_config

```python
get_retry_config(self: Any)
```

Return a tenacity-compatible retry configuration.

**Returns**: A dictionary of kwargs for @retry() decorator.
Example: tenacity.retry(**manager.get_retry_config())

---

#### RateLimitBackoffManager.is_rate_limited

```python
is_rate_limited(self: Any, response_code: int)
```

Check if a response code indicates rate limiting.

**Parameters**:

- `response_code`: HTTP status code (e.g., 429, 503).

**Returns**: True if the code indicates rate limiting, False otherwise.

---

#### RateLimitBackoffManager.make_retry_decorator

```python
make_retry_decorator(self: Any)
```

Create a tenacity retry decorator for this config.

Returns a decorator that retries on rate-limit codes.

---

---

## RateLimitConfig

Configuration for rate-limit backoff behavior.

### Methods

#### RateLimitConfig.validate

```python
validate(self: Any)
```

Validate configuration parameters.

---

---

## compute_wait

```python
compute_wait(self: Any, attempt: int)
```

Compute wait time for a given attempt number.

Uses exponential backoff with jitter:
    wait = min(initial_wait * (multiplier ** attempt) + random_jitter, max_wait)

**Parameters**:

- `attempt`: The attempt number (0-indexed, so first retry is attempt=1).

**Returns**: Wait time in seconds.

---

## get_retry_config

```python
get_retry_config(self: Any)
```

Return a tenacity-compatible retry configuration.

**Returns**: A dictionary of kwargs for @retry() decorator.
Example: tenacity.retry(**manager.get_retry_config())

**Examples**:

```python
>>> manager = RateLimitBackoffManager()
>>> @tenacity.retry(**manager.get_retry_config())
... def call_api():
...     ...
```

---

## is_rate_limited

```python
is_rate_limited(self: Any, response_code: int)
```

Check if a response code indicates rate limiting.

**Parameters**:

- `response_code`: HTTP status code (e.g., 429, 503).

**Returns**: True if the code indicates rate limiting, False otherwise.

---

## make_retry_decorator

```python
make_retry_decorator(self: Any)
```

Create a tenacity retry decorator for this config.

Returns a decorator that retries on rate-limit codes.

**Examples**:

```python
>>> manager = RateLimitBackoffManager()
>>> @manager.make_retry_decorator()
... def call_api():
...     # raises exception with response_code attribute
...     ...
```

---

## validate

```python
validate(self: Any)
```

Validate configuration parameters.

**Raises**:

- `ValueError`: If configuration is invalid.

---

