# delegate API Reference

> **Source**: `src/thegent/teammates/delegate.py`

Task Delegation

Async delegation with status tracking, priority, and timeout handling.

---

## Delegate

Handles task delegation to teammates.

### Methods

#### Delegate.__init__

```python
__init__(self: Any, registry: Optional[TeammateRegistry])
```

---

#### Delegate.cancel

```python
cancel(self: Any, task_id: str)
```

Cancel a delegated task.

---

#### Delegate.delegate

```python
delegate(self: Any, request: DelegationRequest)
```

Delegate task to a teammate.

---

#### Delegate.list_active

```python
list_active(self: Any)
```

List all active tasks.

---

#### Delegate.status

```python
status(self: Any, task_id: str)
```

Get status of delegated task.

---

---

## DelegationRequest

Request to delegate a task.

---

## cancel

```python
cancel(self: Any, task_id: str)
```

Cancel a delegated task.

---

## delegate

```python
delegate(self: Any, request: DelegationRequest)
```

Delegate task to a teammate.

---

## list_active

```python
list_active(self: Any)
```

List all active tasks.

---

## status

```python
status(self: Any, task_id: str)
```

Get status of delegated task.

---

