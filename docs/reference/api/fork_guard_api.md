# fork_guard API Reference

> **Source**: `src/thegent/orchestration/fork_guard.py`

WP-21001: Fork Explosion Guard.
Prevents agent recursion depth and fan-out (parallel sub-tasks) from exceeding safe limits.

---

## ForkContext

Tracks fork state for a specific run and its children.

---

## ForkExplosionGuard

Monitors and limits the creation of sub-tasks to prevent cascading execution.

### Methods

#### ForkExplosionGuard.__init__

```python
__init__(self)
```

#### ForkExplosionGuard.get_stats

Return stats for a specific run.

```python
get_stats(self, run_id)
```

#### ForkExplosionGuard.register_run

Register a new run, inheriting depth from parent.

```python
register_run(self, run_id, parent_id)
```

---

## get_stats

Return stats for a specific run.

```python
get_stats(self, run_id)
```

---

## register_run

Register a new run, inheriting depth from parent.

```python
register_run(self, run_id, parent_id)
```

---

