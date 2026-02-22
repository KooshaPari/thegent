# plan API Reference

> **Source**: `src/thegent/cli/apps/plan.py`

Logical stream: Task and Dependency Planning.

---

## milestone_create

```python
milestone_create(name: Annotated[(str, Any)], product_id: Annotated[(Any, Any)])
```

Create a new milestone in the project registry.

Examples::

    thegent plan milestone create "v1.0"
    thegent plan milestone create "v2.0" --product-id &lt;id&gt;

---

## milestone_list

```python
milestone_list(output_json: Annotated[(bool, Any)])
```

List all milestones.

Examples::

    thegent plan milestone list
    thegent plan milestone list --json

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

## plan_incorporate

```python
plan_incorporate(dry_run: bool)
```

---

## plan_next

```python
plan_next(format: str)
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

## plan_status

```python
plan_status(format: str)
```

---

## plan_work_stream

```python
plan_work_stream(limit: int, format: str, cd: Any)
```

---

## sprint_create

```python
sprint_create(name: Annotated[(str, Any)], milestone_id: Annotated[(Any, Any)])
```

Create a new sprint in the project registry.

Examples::

    thegent plan sprint create "Sprint 1"
    thegent plan sprint create "Sprint 2" --milestone-id &lt;id&gt;

---

## sprint_list

```python
sprint_list(output_json: Annotated[(bool, Any)])
```

List all sprints.

Examples::

    thegent plan sprint list
    thegent plan sprint list --json

---
