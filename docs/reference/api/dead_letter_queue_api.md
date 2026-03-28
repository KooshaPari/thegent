# dead_letter_queue API Reference

> **Source**: `src/thegent/sync/dead_letter_queue.py`

Dead-letter queue utilities for board sync replay with backoff and ordering.

# @trace WL-213

---

## RemoteWriteDeadLetterQueue

Persistent dead-letter queue for board remote writes.

### Methods

#### RemoteWriteDeadLetterQueue.__init__

```python
__init__(self: Any, queue_path: Path)
```

---

#### RemoteWriteDeadLetterQueue.append

```python
append(self: Any, record: RemoteWriteDeadLetterRecord)
```

---

#### RemoteWriteDeadLetterQueue.candidates_for_replay

```python
candidates_for_replay(self: Any)
```

---

#### RemoteWriteDeadLetterQueue.create_entry_id

```python
create_entry_id(self: Any, source: str, board_id: str, item: dict[(str, str)])
```

---

#### RemoteWriteDeadLetterQueue.enqueue

```python
enqueue(self: Any)
```

---

#### RemoteWriteDeadLetterQueue.load

```python
load(self: Any)
```

---

#### RemoteWriteDeadLetterQueue.pending

```python
pending(self: Any)
```

---

#### RemoteWriteDeadLetterQueue.write

```python
write(self: Any, entries: list[RemoteWriteDeadLetterRecord])
```

---

---

## RemoteWriteDeadLetterRecord

Single failed remote-write mutation entry.

**Inherits from**: `SerializableMixin`

### Methods

#### RemoteWriteDeadLetterRecord.can_retry

```python
can_retry(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.first_failed_at_dt

```python
first_failed_at_dt(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.from_dict

```python
from_dict(cls: Any, payload: dict[(str, Any)])
```

---

#### RemoteWriteDeadLetterRecord.is_due

```python
is_due(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.is_pending

```python
is_pending(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.last_attempt_at_dt

```python
last_attempt_at_dt(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.mark_failed

```python
mark_failed(self: Any)
```

---

#### RemoteWriteDeadLetterRecord.mark_success

```python
mark_success(self: Any, now: datetime)
```

---

#### RemoteWriteDeadLetterRecord.next_attempt_at_dt

```python
next_attempt_at_dt(self: Any)
```

---

---

## append

```python
append(self: Any, record: RemoteWriteDeadLetterRecord) -> None
```

---

## can_retry

```python
can_retry(self: Any) -> bool
```

---

## candidates_for_replay

```python
candidates_for_replay(self: Any) -> list[RemoteWriteDeadLetterRecord]
```

---

## compute_backoff_seconds

```python
compute_backoff_seconds(attempt: int)
```

Compute deterministic retry delay in seconds for a given attempt number.

---

## create_entry_id

```python
create_entry_id(self: Any, source: str, board_id: str, item: dict[(str, str)]) -> str
```

---

## enqueue

```python
enqueue(self: Any) -> RemoteWriteDeadLetterRecord
```

---

## first_failed_at_dt

```python
first_failed_at_dt(self: Any) -> datetime
```

---

## from_dict

```python
from_dict(cls: Any, payload: dict[(str, Any)]) -> RemoteWriteDeadLetterRecord
```

---

## is_due

```python
is_due(self: Any) -> bool
```

---

## is_pending

```python
is_pending(self: Any) -> bool
```

---

## last_attempt_at_dt

```python
last_attempt_at_dt(self: Any) -> Any
```

---

## load

```python
load(self: Any) -> list[RemoteWriteDeadLetterRecord]
```

---

## mark_failed

```python
mark_failed(self: Any) -> RemoteWriteDeadLetterRecord
```

---

## mark_success

```python
mark_success(self: Any, now: datetime) -> RemoteWriteDeadLetterRecord
```

---

## next_attempt_at_dt

```python
next_attempt_at_dt(self: Any) -> datetime
```

---

## pending

```python
pending(self: Any) -> list[RemoteWriteDeadLetterRecord]
```

---

## write

```python
write(self: Any, entries: list[RemoteWriteDeadLetterRecord]) -> None
```

---

