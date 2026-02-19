# failure_modes API Reference

> **Source**: `src/thegent/orchestration/failure_modes.py`

MAST 14-mode failure taxonomy (WP-2005, FR-007).

---

## FailureMode

MAST 14-mode failure taxonomy for classification and recovery.

**Inherits from**: `str, Enum`

---

## classify_failure

Classify failure from error message to MAST mode.

```python
classify_failure(error_message)
```

---

