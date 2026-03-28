# async_utils API Reference

> **Source**: `src/thegent/utils/async_utils.py`

Async utilities for thegent.

Common async patterns and helpers.

---

## AsyncBatch

Batch processor for async operations.

### Methods

#### AsyncBatch.__init__

```python
__init__(self: Any, batch_size: int, delay: float)
```

---

---

## async_retry

```python
async_retry(max_attempts: int, delay: float, backoff: float, exceptions: tuple)
```

Decorator for retrying async functions.

**Parameters**:

- `max_attempts`: Maximum number of attempts
- `delay`: Initial delay between retries
- `backoff`: Backoff multiplier
- `exceptions`: Tuple of exceptions to catch

**Examples**:

```python
@async_retry(max_attempts=3, delay=1.0)
async def fetch(url: str) -> str:
    ...
```

---

## decorator

```python
decorator(func: Callable[(Ellipsis, Awaitable[T])]) -> Callable[(Ellipsis, Awaitable[T])]
```

---

