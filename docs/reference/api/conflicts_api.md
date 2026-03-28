# conflicts API Reference

> **Source**: `src/thegent/sync/conflicts.py`

Conflict surfacing helpers for sync operations.

# @trace WL-204

---

## SyncConflict

A single unresolved sync conflict.

---

## recommend_action

```python
recommend_action(conflict: SyncConflict)
```

Return a deterministic resolution recommendation.

---

## render_conflict_surface

```python
render_conflict_surface(conflicts: list[SyncConflict])
```

Render stable one-line conflict summaries for CLI output.

---

## unresolved_conflicts

```python
unresolved_conflicts(conflicts: list[SyncConflict]) -> list[SyncConflict]
```

---

