# plan API Reference

> **Source**: `src/thegent/cli/apps/plan.py`

Logical stream: Task and Dependency Planning.

---

## plan_add

```python
plan_add(task_id: str, agent: str, prompt: str, depends_on: Any)
```

---

## plan_analyze

```python
plan_analyze(cd: Any, format: str)
```

---

## plan_checkpoint

```python
plan_checkpoint(reason: str)
```

---

## plan_claim

```python
plan_claim(item_id: str, agent_id: Any, cd: Any)
```

---

## plan_complete

```python
plan_complete(item_id: str, agent_id: Any, cd: Any)
```

---

## plan_harness_status

```python
plan_harness_status(format: str)
```

Get status of all harness hosts.

---

## plan_incorporate

```python
plan_incorporate(dry_run: bool)
```

---

## plan_lint_workstream

```python
plan_lint_workstream(cd: Any) -> None
```

---

## plan_next

```python
plan_next(format: str)
```

---

## plan_normalize_workstream

```python
plan_normalize_workstream(cd: Any) -> None
```

---

## plan_progress

```python
plan_progress(limit: int, format: str)
```

---

## plan_remove

```python
plan_remove(task_id: str)
```

---

## plan_roadmap

```python
plan_roadmap(format: str)
```

---

## plan_rollback

```python
plan_rollback(checkpoint_id: str)
```

---

## plan_sessions

```python
plan_sessions(harness: Any, format: str)
```

List sessions from all agent harnesses.

---

## plan_status

```python
plan_status(format: str)
```

---

## plan_verify_workstream

```python
plan_verify_workstream(cd: Any, format: str)
```

---

## plan_work_stream

```python
plan_work_stream(limit: int, format: str)
```

---

