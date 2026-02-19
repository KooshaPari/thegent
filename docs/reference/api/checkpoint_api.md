# checkpoint API Reference

> **Source**: `src/thegent/orchestration/checkpoint.py`

Checkpoint/rollback service ops (WP-2001, FR-006).

---

## create

Create a checkpoint.

```python
create(session_dir, reason, dag_content, owner)
```

---

## get

Retrieve a checkpoint by ID.

```python
get(session_dir, checkpoint_id)
```

---

## list_checkpoints

List recent checkpoints.

```python
list_checkpoints(session_dir, limit)
```

---

