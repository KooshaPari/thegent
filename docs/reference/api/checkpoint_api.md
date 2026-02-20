# checkpoint API Reference

> **Source**: `src/thegent/orchestration/checkpoint.py`

Checkpoint/rollback service ops (WP-2001, FR-006).

---

## create

```python
create(session_dir: Path, reason: str, dag_content: str, owner: str)
```

Create a checkpoint.

---

## get

```python
get(session_dir: Path, checkpoint_id: str)
```

Retrieve a checkpoint by ID.

---

## list_checkpoints

```python
list_checkpoints(session_dir: Path, limit: int)
```

List recent checkpoints.

---

