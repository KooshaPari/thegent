# cliproxy_error_utils API Reference

> **Source**: `src/thegent/cliproxy_error_utils.py`

## InsufficientCreditsError

OR-13: Raised when OpenRouter returns HTTP 402 (insufficient credits).

MUST NOT be retried — callers must surface this error to the user immediately.

**Inherits from**: `RuntimeError`

---

## _RetryableStreamError

OR-13: Internal signal that the stream got a retryable HTTP error (408/502/503).

**Inherits from**: `Exception`

### Methods

#### _RetryableStreamError.__init__

```python
__init__(self: Any, status_code: int, raw_body: bytes)
```

---

---

