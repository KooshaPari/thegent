# provider_loop API Reference

> **Source**: `src/thegent/agents/provider_loop.py`

WP-2003: Provider loop time bounds (max 5 min by default).

Provides PROVIDER_LOOP_TIMEOUT_SEC and the async helper run_with_provider_loop_timeout()
that wraps any coroutine with asyncio.wait_for and raises ProviderLoopTimeout on expiry.

Fail fast: asyncio.TimeoutError is NEVER swallowed silently — it is always re-raised
as ProviderLoopTimeout with full log context.

# @trace WL-039 WP-2003

---

## ProviderLoopTimeout

Raised when the provider selection + retry loop exceeds PROVIDER_LOOP_TIMEOUT_SEC.

Callers MUST NOT swallow this silently.  Log the event, surface the error,
and abort the current run.

**Inherits from**: `Exception`

### Methods

#### ProviderLoopTimeout.__init__

```python
__init__(self: Any, timeout_sec: int, context: str)
```

---

---

