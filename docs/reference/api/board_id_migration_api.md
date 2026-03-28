# board_id_migration API Reference

> **Source**: `src/thegent/integrations/board_id_migration.py`

## LegacyBoardIdMigrationTool

Tool for managing legacy board ID migrations.

# @trace WL-247

### Methods

#### LegacyBoardIdMigrationTool.__init__

```python
__init__(self: Any)
```

Initialize the migration tool with an empty registry.

---

#### LegacyBoardIdMigrationTool.completed

```python
completed(self: Any)
```

Get all completed migrations.

**Returns**: List of MigrationEntry objects with migrated=True

---

#### LegacyBoardIdMigrationTool.lookup_new

```python
lookup_new(self: Any, old_id: str)
```

Look up the new board ID for a legacy ID.

**Parameters**:

- `old_id`: The legacy board ID

**Returns**: The new board ID

---

#### LegacyBoardIdMigrationTool.migrate

```python
migrate(self: Any, old_id: str)
```

Mark a migration as complete.

**Parameters**:

- `old_id`: The legacy board ID to mark as migrated

**Returns**: The updated MigrationEntry

---

#### LegacyBoardIdMigrationTool.pending

```python
pending(self: Any)
```

Get all pending (not yet migrated) entries.

**Returns**: List of MigrationEntry objects with migrated=False

---

#### LegacyBoardIdMigrationTool.register

```python
register(self: Any, old_id: str, new_id: str)
```

Register a new migration entry.

**Parameters**:

- `old_id`: The legacy board ID
- `new_id`: The new board ID

**Returns**: The created MigrationEntry

---

---

## MigrationEntry

Represents a single board ID migration record.

---

## completed

```python
completed(self: Any)
```

Get all completed migrations.

**Returns**: List of MigrationEntry objects with migrated=True

---

## lookup_new

```python
lookup_new(self: Any, old_id: str)
```

Look up the new board ID for a legacy ID.

**Parameters**:

- `old_id`: The legacy board ID

**Returns**: The new board ID

**Raises**:

- `KeyError`: If the old_id is not registered

---

## migrate

```python
migrate(self: Any, old_id: str)
```

Mark a migration as complete.

**Parameters**:

- `old_id`: The legacy board ID to mark as migrated

**Returns**: The updated MigrationEntry

**Raises**:

- `KeyError`: If the old_id is not registered

---

## pending

```python
pending(self: Any)
```

Get all pending (not yet migrated) entries.

**Returns**: List of MigrationEntry objects with migrated=False

---

## register

```python
register(self: Any, old_id: str, new_id: str)
```

Register a new migration entry.

**Parameters**:

- `old_id`: The legacy board ID
- `new_id`: The new board ID

**Returns**: The created MigrationEntry

---

