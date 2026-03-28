# task API Reference

> **Source**: `src/thegent/agents/crew/task.py`

Task data model with dependency support.

---

## Task

Task definition with dependencies.

Tasks can depend on other tasks, forming a DAG that is resolved
topologically before execution.

### Methods

#### Task.add_dependency

```python
add_dependency(self: Any, task_id: str)
```

Add a dependency on another task.

---

#### Task.is_ready

```python
is_ready(self: Any, completed_tasks: set[str])
```

Check if all dependencies are completed.

---

#### Task.mark_completed

```python
mark_completed(self: Any, result: Any)
```

Mark task as completed.

---

#### Task.mark_failed

```python
mark_failed(self: Any, error: str)
```

Mark task as failed.

---

#### Task.mark_running

```python
mark_running(self: Any)
```

Mark task as running.

---

#### Task.remove_dependency

```python
remove_dependency(self: Any, task_id: str)
```

Remove a dependency.

---

---

## TaskStatus

Task execution status.

**Inherits from**: `StrEnum`

---

## add_dependency

```python
add_dependency(self: Any, task_id: str)
```

Add a dependency on another task.

---

## is_ready

```python
is_ready(self: Any, completed_tasks: set[str])
```

Check if all dependencies are completed.

---

## mark_completed

```python
mark_completed(self: Any, result: Any)
```

Mark task as completed.

---

## mark_failed

```python
mark_failed(self: Any, error: str)
```

Mark task as failed.

---

## mark_running

```python
mark_running(self: Any)
```

Mark task as running.

---

## remove_dependency

```python
remove_dependency(self: Any, task_id: str)
```

Remove a dependency.

---

