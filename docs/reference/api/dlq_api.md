# dlq API Reference

> **Source**: `src/thegent/orchestration/dlq.py`

Dead-letter queue service (WP-Y2, FR-034).

---

## is_poison_pill

True if run has failed threshold+ times (poison pill).

```python
is_poison_pill(session_dir, run_id, threshold)
```

---

## list_pending

List DLQ items pending review.

```python
list_pending(session_dir, limit)
```

---

## resolve

Mark DLQ item as resolved (replayed, fixed, discarded).

```python
resolve(session_dir, run_id, resolution)
```

---

