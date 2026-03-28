# retry_helpers API Reference

> **Source**: `src/thegent/cli/services/retry_helpers.py`

Retry helper services extracted from cli.commands.impl (WL-125).

---

## backoff_delay

```python
backoff_delay(attempt: int, max_delay: float)
```

Return a capped exponential-jitter retry delay in seconds.

---

