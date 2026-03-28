# workstream_ops API Reference

> **Source**: `src/thegent/utils/workstream_ops.py`

Automated work stream operations (read, parse, update).

---

## WorkStreamOps

Automated operations on work stream files.

### Methods

#### WorkStreamOps.__init__

```python
__init__(self: Any, base_dir: Any)
```

Initialize work stream operations.

**Parameters**:

- `base_dir`: Base directory for work stream files

---

#### WorkStreamOps.claim_item

```python
claim_item(self: Any, item_id: str, agent_id: str)
```

Claim an item by adding it to CLAIMED section.

**Parameters**:

- `item_id`: Work item ID
- `agent_id`: Agent identifier

**Returns**: True if successful

---

#### WorkStreamOps.complete_item

```python
complete_item(self: Any, item_id: str, agent_id: str)
```

Mark an item as complete.

**Parameters**:

- `item_id`: Work item ID
- `agent_id`: Agent identifier

**Returns**: True if successful

---

#### WorkStreamOps.find_work_stream

```python
find_work_stream(self: Any)
```

Find the work stream file in common locations.

---

#### WorkStreamOps.get_progress

```python
get_progress(self: Any)
```

Calculate progress statistics.

**Returns**: Dictionary with counts of total, completed, and backlog items.

---

#### WorkStreamOps.lint_schema

```python
lint_schema(self: Any)
```

Return structural schema lint errors for the current WORK_STREAM file.

---

#### WorkStreamOps.read_backlog

```python
read_backlog(self: Any)
```

Read all items from BACKLOG section.

**Returns**: List of backlog items with id, title, priority, depends

---

#### WorkStreamOps.sort_and_normalize

```python
sort_and_normalize(self: Any)
```

Sort WL sections and normalize status formatting.

---

---

## claim_item

```python
claim_item(self: Any, item_id: str, agent_id: str)
```

Claim an item by adding it to CLAIMED section.

**Parameters**:

- `item_id`: Work item ID
- `agent_id`: Agent identifier

**Returns**: True if successful

---

## complete_item

```python
complete_item(self: Any, item_id: str, agent_id: str)
```

Mark an item as complete.

**Parameters**:

- `item_id`: Work item ID
- `agent_id`: Agent identifier

**Returns**: True if successful

---

## find_work_stream

```python
find_work_stream(self: Any)
```

Find the work stream file in common locations.

---

## get_progress

```python
get_progress(self: Any)
```

Calculate progress statistics.

**Returns**: Dictionary with counts of total, completed, and backlog items.

---

## lint_schema

```python
lint_schema(self: Any)
```

Return structural schema lint errors for the current WORK_STREAM file.

---

## read_backlog

```python
read_backlog(self: Any)
```

Read all items from BACKLOG section.

**Returns**: List of backlog items with id, title, priority, depends

---

## sort_and_normalize

```python
sort_and_normalize(self: Any)
```

Sort WL sections and normalize status formatting.

---

