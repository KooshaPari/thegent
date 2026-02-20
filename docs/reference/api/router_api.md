# router API Reference

> **Source**: `src/thegent/orchestration/router.py`

WP-1001: Dependency-aware routing engine (FR-001).

---

## DependencyRouter

Dependency-aware routing engine for multi-task orchestration.

### Methods

#### DependencyRouter.from_tasks

```python
from_tasks(cls: Any, tasks: list[dict[str, Any]])
```

Factory: Create router from a list of tasks with 'id' and 'depends_on'.

---

#### DependencyRouter.get_ready_tasks

```python
get_ready_tasks(self: Any)
```

Return task IDs that are ready to run (dependencies satisfied).

---

#### DependencyRouter.is_finished

```python
is_finished(self: Any)
```

Return True if all tasks in the DAG are completed.

---

#### DependencyRouter.mark_completed

```python
mark_completed(self: Any, task_id: str)
```

Mark a task as completed and update the sorter.

---

#### DependencyRouter.mark_started

```python
mark_started(self: Any, task_id: str)
```

Mark a task as running.

---

---

## from_tasks

```python
from_tasks(cls: Any, tasks: list[dict[str, Any]])
```

Factory: Create router from a list of tasks with 'id' and 'depends_on'.

---

## get_ready_tasks

```python
get_ready_tasks(self: Any)
```

Return task IDs that are ready to run (dependencies satisfied).

---

## is_finished

```python
is_finished(self: Any)
```

Return True if all tasks in the DAG are completed.

---

## mark_completed

```python
mark_completed(self: Any, task_id: str)
```

Mark a task as completed and update the sorter.

---

## mark_started

```python
mark_started(self: Any, task_id: str)
```

Mark a task as running.

---

