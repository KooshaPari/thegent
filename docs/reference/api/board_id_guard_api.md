# board_id_guard API Reference

> **Source**: `src/thegent/integrations/board_id_guard.py`

Board-ID Collision Guard for workstream sync integrity.

# @trace WL-183

---

## BoardIdCollisionError

Exception raised when board ID collisions are detected.

**Inherits from**: `Exception`

---

## BoardIdRegistry

Registry for tracking board IDs across connectors.

### Methods

#### BoardIdRegistry.__init__

```python
__init__(self: Any)
```

Initialize the board ID registry.

---

#### BoardIdRegistry.check_collision

```python
check_collision(self: Any, board_id: str)
```

Check if a board ID exists in the registry.

**Parameters**:

- `board_id`: The board ID to check.

**Returns**: True if board_id is already registered, False otherwise.

---

#### BoardIdRegistry.clear

```python
clear(self: Any)
```

Clear all registered board IDs.

---

#### BoardIdRegistry.get_all

```python
get_all(self: Any)
```

Get all registered board IDs and their connectors.

**Returns**: Dictionary mapping board_id -> connector_name.

---

#### BoardIdRegistry.register

```python
register(self: Any, board_id: str, connector: str)
```

Register a board ID for a connector.

**Parameters**:

- `board_id`: The board ID to register.
- `connector`: The connector name.

---

---

## check_collision

```python
check_collision(self: Any, board_id: str)
```

Check if a board ID exists in the registry.

**Parameters**:

- `board_id`: The board ID to check.

**Returns**: True if board_id is already registered, False otherwise.

---

## clear

```python
clear(self: Any)
```

Clear all registered board IDs.

---

## get_all

```python
get_all(self: Any)
```

Get all registered board IDs and their connectors.

**Returns**: Dictionary mapping board_id -> connector_name.

---

## migrate_legacy_board_id

```python
migrate_legacy_board_id(legacy_id: str)
```

Convert legacy board IDs to canonical WL namespace IDs.

---

## register

```python
register(self: Any, board_id: str, connector: str)
```

Register a board ID for a connector.

**Parameters**:

- `board_id`: The board ID to register.
- `connector`: The connector name.

**Raises**:

- `BoardIdCollisionError`: If board_id is already registered with a different connector.

---

## validate_no_collisions

```python
validate_no_collisions(registry: BoardIdRegistry)
```

Validate that no duplicate board IDs exist across connectors.

**Parameters**:

- `registry`: The BoardIdRegistry to validate.

**Raises**:

- `BoardIdCollisionError`: If duplicate board IDs are detected.

---

