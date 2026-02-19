# router API Reference

> **Source**: `src/thegent/orchestration/router.py`

WP-1001: Dependency-aware routing engine (FR-001).

---

## DependencyRouter

Dependency-aware routing engine for multi-task orchestration.

### Methods

#### DependencyRouter.__init__

Initialize with a DAG: task_id -> list of dependency task_ids.
Example: {'B': ['A'], 'C': ['A'], 'D': ['B', 'C']}

```python
__init__(self, dag)
```

#### DependencyRouter.from_tasks

Factory: Create router from a list of tasks with 'id' and 'depends_on'.

```python
from_tasks(cls, tasks)
```

#### DependencyRouter.get_ready_tasks

Return task IDs that are ready to run (dependencies satisfied).

```python
get_ready_tasks(self)
```

#### DependencyRouter.is_finished

Return True if all tasks in the DAG are completed.

```python
is_finished(self)
```

#### DependencyRouter.mark_completed

Mark a task as completed and update the sorter.

```python
mark_completed(self, task_id)
```

#### DependencyRouter.mark_started

Mark a task as running.

```python
mark_started(self, task_id)
```

---

## from_tasks

Factory: Create router from a list of tasks with 'id' and 'depends_on'.

```python
from_tasks(cls, tasks)
```

---

## get_ready_tasks

Return task IDs that are ready to run (dependencies satisfied).

```python
get_ready_tasks(self)
```

---

## is_finished

Return True if all tasks in the DAG are completed.

```python
is_finished(self)
```

---

## mark_completed

Mark a task as completed and update the sorter.

```python
mark_completed(self, task_id)
```

---

## mark_started

Mark a task as running.

```python
mark_started(self, task_id)
```

---

