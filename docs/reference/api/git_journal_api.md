# git_journal API Reference

> **Source**: `src/thegent/audit/git_journal.py`

Git journal classes for shadow audit.

Extracted from shadow_audit_git.py for maintainability.

---

## GitJournal

Git-based journal for audit trails.

Stores audit entries as JSON files in a git-tracked directory.

### Methods

#### GitJournal.__init__

```python
__init__(self: Any, journal_dir: Any)
```

Initialize the journal.

**Parameters**:

- `journal_dir`: Directory to store journal entries

---

#### GitJournal.add_entry

```python
add_entry(self: Any, agent: str, action: str, target: str, result: str, metadata: Any)
```

Add a journal entry.

**Parameters**:

- `agent`: Agent that performed the action
- `action`: Action performed
- `target`: Target of the action
- `result`: Result of the action
- `metadata`: Optional additional metadata

**Returns**: The created entry

---

#### GitJournal.commit

```python
commit(self: Any, message: str)
```

Commit journal changes to git.

**Parameters**:

- `message`: Commit message

**Returns**: True if successful

---

#### GitJournal.get_entry

```python
get_entry(self: Any, entry_id: str)
```

Get an entry by ID.

**Parameters**:

- `entry_id`: Entry ID

**Returns**: Entry or None if not found

---

#### GitJournal.list_entries

```python
list_entries(self: Any, agent: Any, action: Any, limit: int)
```

List journal entries.

**Parameters**:

- `agent`: Filter by agent
- `action`: Filter by action
- `limit`: Maximum entries to return

**Returns**: List of entries

---

---

## JournalEntry

A single journal entry.

### Methods

#### JournalEntry.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create from dictionary.

---

#### JournalEntry.to_dict

```python
to_dict(self: Any)
```

Convert to dictionary.

---

---

## add_entry

```python
add_entry(self: Any, agent: str, action: str, target: str, result: str, metadata: Any)
```

Add a journal entry.

**Parameters**:

- `agent`: Agent that performed the action
- `action`: Action performed
- `target`: Target of the action
- `result`: Result of the action
- `metadata`: Optional additional metadata

**Returns**: The created entry

---

## commit

```python
commit(self: Any, message: str)
```

Commit journal changes to git.

**Parameters**:

- `message`: Commit message

**Returns**: True if successful

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create from dictionary.

---

## get_entry

```python
get_entry(self: Any, entry_id: str)
```

Get an entry by ID.

**Parameters**:

- `entry_id`: Entry ID

**Returns**: Entry or None if not found

---

## list_entries

```python
list_entries(self: Any, agent: Any, action: Any, limit: int)
```

List journal entries.

**Parameters**:

- `agent`: Filter by agent
- `action`: Filter by action
- `limit`: Maximum entries to return

**Returns**: List of entries

---

## to_dict

```python
to_dict(self: Any)
```

Convert to dictionary.

---

