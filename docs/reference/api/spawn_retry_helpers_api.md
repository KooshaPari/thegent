# spawn_retry_helpers API Reference

> **Source**: `src/thegent/cli/services/spawn_retry_helpers.py`

Spawn retry helper services extracted from cli.commands.impl (WL-125).

---

## retry_if_eagain

```python
retry_if_eagain(exc: BaseException)
```

Return True when *exc* is an OSError due to EAGAIN/EWOULDBLOCK.

---

