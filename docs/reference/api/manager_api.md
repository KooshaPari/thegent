# manager API Reference

> **Source**: `src/thegent/session/manager.py`

In-memory SessionManager scaffolding for fork/rollback APIs (WL-106).

---

## InvalidTurnIndexError

Raised when a fork index is outside valid bounds.

**Inherits from**: `SessionManagerError`

**Method Resolution Order**: `InvalidTurnIndexError -> SessionManagerError`

---

## RollbackOutOfRangeError

Raised when rollback exceeds available history.

**Inherits from**: `SessionManagerError`

**Method Resolution Order**: `RollbackOutOfRangeError -> SessionManagerError`

---

## SessionAlreadyExistsError

Raised when creating/forking into an existing session ID.

**Inherits from**: `SessionManagerError`

**Method Resolution Order**: `SessionAlreadyExistsError -> SessionManagerError`

---

## SessionManager

Minimal in-memory session registry with fork/rollback APIs.

### Methods

#### SessionManager.__init__

```python
__init__(self: Any)
```

---

#### SessionManager.append_turn

```python
append_turn(self: Any, session_id: str, turn: dict[(str, Any)])
```

---

#### SessionManager.create_session

```python
create_session(self: Any)
```

---

#### SessionManager.fork_session

```python
fork_session(self: Any, session_id: str)
```

---

#### SessionManager.get_session

```python
get_session(self: Any, session_id: str)
```

---

#### SessionManager.rollback_session

```python
rollback_session(self: Any, session_id: str)
```

---

---

## SessionManagerError

Base exception for session manager failures.

**Inherits from**: `RuntimeError`

---

## SessionNotFoundError

Raised when a session ID does not exist.

**Inherits from**: `SessionManagerError`

**Method Resolution Order**: `SessionNotFoundError -> SessionManagerError`

---

## SessionState

---

## append_turn

```python
append_turn(self: Any, session_id: str, turn: dict[(str, Any)]) -> int
```

---

## create_session

```python
create_session(self: Any) -> str
```

---

## fork_session

```python
fork_session(self: Any, session_id: str) -> str
```

---

## get_session

```python
get_session(self: Any, session_id: str) -> SessionState
```

---

## rollback_session

```python
rollback_session(self: Any, session_id: str) -> int
```

---

