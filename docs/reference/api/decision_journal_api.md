# decision_journal API Reference

> **Source**: `src/thegent/integrations/decision_journal.py`

Local decision journal for recording work stream decisions and replay capability.

# @trace WL-203

---

## DecisionJournal

Journal for recording and replaying decisions made to work stream items.

### Methods

#### DecisionJournal.__init__

```python
__init__(self: Any, journal_file: Any)
```

Initialize the decision journal.

**Parameters**:

- `journal_file`: Path to JSONL journal file. Defaults to
docs/reference/decision_journal.jsonl.

---

#### DecisionJournal.append

```python
append(self: Any, entry: JournalEntry)
```

Record a decision in the journal.

Appends a JSON-serialized entry to the JSONL file.

**Parameters**:

- `entry`: JournalEntry to record.

---

#### DecisionJournal.read_all

```python
read_all(self: Any)
```

Read all entries from the journal.

**Returns**: List of JournalEntry objects, in order of appearance.

---

#### DecisionJournal.read_replayable

```python
read_replayable(self: Any)
```

Read only replayable entries from the journal.

**Returns**: List of JournalEntry objects where replayable=True.

---

#### DecisionJournal.replay_entry

```python
replay_entry(self: Any, entry_id: str)
```

Retrieve a specific entry by ID for replay.

**Parameters**:

- `entry_id`: Entry ID to retrieve.

**Returns**: The matching JournalEntry.

---

---

## JournalEntry

Record of a decision made during a work stream cycle.

### Methods

#### JournalEntry.create_entry

```python
create_entry(cycle_id: str, wl_id: str, decision: str, rationale: str, before_state: dict[(str, Any)], after_state: dict[(str, Any)], replayable: bool)
```

Factory method to create a new JournalEntry.

**Parameters**:

- `cycle_id`: Associated cycle ID.
- `wl_id`: Work stream item ID.
- `decision`: Decision type/name.
- `rationale`: Explanation.
- `before_state`: State before decision.
- `after_state`: State after decision.
- `replayable`: Whether the decision can be replayed (default: True).

**Returns**: A new JournalEntry with auto-generated ID and timestamp.

---

---

## append

```python
append(self: Any, entry: JournalEntry)
```

Record a decision in the journal.

Appends a JSON-serialized entry to the JSONL file.

**Parameters**:

- `entry`: JournalEntry to record.

---

## create_entry

```python
create_entry(cycle_id: str, wl_id: str, decision: str, rationale: str, before_state: dict[(str, Any)], after_state: dict[(str, Any)], replayable: bool)
```

Factory method to create a new JournalEntry.

**Parameters**:

- `cycle_id`: Associated cycle ID.
- `wl_id`: Work stream item ID.
- `decision`: Decision type/name.
- `rationale`: Explanation.
- `before_state`: State before decision.
- `after_state`: State after decision.
- `replayable`: Whether the decision can be replayed (default: True).

**Returns**: A new JournalEntry with auto-generated ID and timestamp.

---

## read_all

```python
read_all(self: Any)
```

Read all entries from the journal.

**Returns**: List of JournalEntry objects, in order of appearance.

---

## read_replayable

```python
read_replayable(self: Any)
```

Read only replayable entries from the journal.

**Returns**: List of JournalEntry objects where replayable=True.

---

## replay_entry

```python
replay_entry(self: Any, entry_id: str)
```

Retrieve a specific entry by ID for replay.

**Parameters**:

- `entry_id`: Entry ID to retrieve.

**Returns**: The matching JournalEntry.

**Raises**:

- `ValueError`: If entry is not found.

---

