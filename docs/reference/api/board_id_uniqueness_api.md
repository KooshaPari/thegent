# board_id_uniqueness API Reference

> **Source**: `src/thegent/integrations/board_id_uniqueness.py`

Strict board ID uniqueness enforcement.

# @trace WL-309

---

## BoardIdUniquenessPolicy

Policy for enforcing board ID uniqueness.

---

## DuplicateBoardIdError

Raised when a duplicate board ID is registered.

**Inherits from**: `Exception`

---

## UniquenesEnforcer

Enforce strict board ID uniqueness across all sync artifacts.

### Methods

#### UniquenesEnforcer.__init__

```python
__init__(self: Any, policy: Any)
```

Initialize the uniqueness enforcer.

**Parameters**:

- `policy`: BoardIdUniquenessPolicy instance (default: BoardIdUniquenessPolicy()).

---

#### UniquenesEnforcer.is_registered

```python
is_registered(self: Any, board_id: str)
```

Check if a board ID is already registered.

**Parameters**:

- `board_id`: The board ID to check.

**Returns**: True if the board ID is registered, False otherwise.

---

#### UniquenesEnforcer.register_id

```python
register_id(self: Any, board_id: str, _context: Any)
```

Register a board ID and enforce uniqueness.

**Parameters**:

- `board_id`: The board ID to register.
- `_context`: Optional context information for the registration.

---

#### UniquenesEnforcer.reset

```python
reset(self: Any)
```

Clear all registered board IDs.

This method resets the registry to an empty state.

---

---

## is_registered

```python
is_registered(self: Any, board_id: str)
```

Check if a board ID is already registered.

**Parameters**:

- `board_id`: The board ID to check.

**Returns**: True if the board ID is registered, False otherwise.

---

## register_id

```python
register_id(self: Any, board_id: str, _context: Any)
```

Register a board ID and enforce uniqueness.

**Parameters**:

- `board_id`: The board ID to register.
- `_context`: Optional context information for the registration.

**Raises**:

- `DuplicateBoardIdError`: If the board ID is already registered
and enforce_global_uniqueness is True.

---

## reset

```python
reset(self: Any)
```

Clear all registered board IDs.

This method resets the registry to an empty state.

---

## validate_unique_board_ids

```python
validate_unique_board_ids(board_ids: list[str])
```

Validate a list of canonical board IDs is globally unique.

---

