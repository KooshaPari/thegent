# journal API Reference

> **Source**: `src/thegent/sync/journal.py`

Local sync decision journal primitives.

# @trace WL-203

---

## LocalDecisionJournal

Strict JSONL journal for sync decision replay.

### Methods

#### LocalDecisionJournal.__init__

```python
__init__(self: Any, path: Path)
```

---

#### LocalDecisionJournal.append

```python
append(self: Any, entry: SyncDecisionEntry)
```

---

#### LocalDecisionJournal.path

```python
path(self: Any)
```

---

#### LocalDecisionJournal.read_all

```python
read_all(self: Any)
```

---

#### LocalDecisionJournal.read_replayable

```python
read_replayable(self: Any)
```

---

---

## SyncDecisionEntry

A replayable decision made during a sync cycle.

### Methods

#### SyncDecisionEntry.create

```python
create(cls: Any)
```

---

---

## append

```python
append(self: Any, entry: SyncDecisionEntry) -> None
```

---

## create

```python
create(cls: Any) -> SyncDecisionEntry
```

---

## path

```python
path(self: Any) -> Path
```

---

## read_all

```python
read_all(self: Any) -> list[SyncDecisionEntry]
```

---

## read_replayable

```python
read_replayable(self: Any) -> list[SyncDecisionEntry]
```

---

