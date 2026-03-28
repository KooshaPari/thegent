# conflict_queue API Reference

> **Source**: `src/thegent/integrations/conflict_queue.py`

Manual Conflict Queue for resolving workstream conflicts.

Queues conflicts for manual resolution and tracks resolution status.

# @trace WL-205

---

## ConflictEntry

Represents a single conflict in the queue.

---

## ConflictQueue

Queue for managing conflicts requiring manual resolution.

Maintains a FIFO queue of conflicts and tracks their resolution status.

### Methods

#### ConflictQueue.__init__

```python
__init__(self: Any)
```

Initialize an empty conflict queue.

---

#### ConflictQueue.all_entries

```python
all_entries(self: Any)
```

Get all conflicts (resolved and unresolved) in insertion order.

**Returns**: List of all ConflictEntry objects.

---

#### ConflictQueue.dequeue

```python
dequeue(self: Any)
```

Remove and return the first unresolved conflict from the queue.

**Returns**: The next unresolved ConflictEntry in FIFO order.

---

#### ConflictQueue.enqueue

```python
enqueue(self: Any, entry: ConflictEntry)
```

Add a conflict to the queue.

**Parameters**:

- `entry`: The ConflictEntry to enqueue.

---

#### ConflictQueue.pending

```python
pending(self: Any)
```

Get all unresolved conflicts in FIFO order.

**Returns**: List of unresolved ConflictEntry objects.

---

#### ConflictQueue.resolve

```python
resolve(self: Any, conflict_id: str)
```

Mark a conflict as resolved.

**Parameters**:

- `conflict_id`: The ID of the conflict to mark as resolved.

---

#### ConflictQueue.size

```python
size(self: Any)
```

Get the count of unresolved (pending) conflicts.

**Returns**: Number of pending conflicts.

---

---

## all_entries

```python
all_entries(self: Any)
```

Get all conflicts (resolved and unresolved) in insertion order.

**Returns**: List of all ConflictEntry objects.

---

## classify_conflict

Classify conflict routing fields deterministically.

---

## dequeue

```python
dequeue(self: Any)
```

Remove and return the first unresolved conflict from the queue.

**Returns**: The next unresolved ConflictEntry in FIFO order.

**Raises**:

- `IndexError`: If the queue is empty (no unresolved conflicts).

---

## enqueue

```python
enqueue(self: Any, entry: ConflictEntry)
```

Add a conflict to the queue.

**Parameters**:

- `entry`: The ConflictEntry to enqueue.

**Raises**:

- `ValueError`: If entry is None or if conflict_id is empty.

---

## pending

```python
pending(self: Any)
```

Get all unresolved conflicts in FIFO order.

**Returns**: List of unresolved ConflictEntry objects.

---

## resolve

```python
resolve(self: Any, conflict_id: str)
```

Mark a conflict as resolved.

**Parameters**:

- `conflict_id`: The ID of the conflict to mark as resolved.

**Raises**:

- `KeyError`: If the conflict_id is not found in the queue.

---

## size

```python
size(self: Any)
```

Get the count of unresolved (pending) conflicts.

**Returns**: Number of pending conflicts.

---

