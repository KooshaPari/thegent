# dlq API Reference

> **Source**: `src/thegent/orchestration/resilience/dlq.py`

Dead-letter queue service (WP-Y2, FR-034).

---

## is_poison_pill

```python
is_poison_pill(session_dir: Path, run_id: str, threshold: int)
```

True if run has failed threshold+ times (poison pill).

---

## list_pending

```python
list_pending(session_dir: Path, limit: int)
```

List DLQ items pending review.

---

## resolve

```python
resolve(session_dir: Path, run_id: str, resolution: str)
```

Mark DLQ item as resolved (replayed, fixed, discarded).

---

