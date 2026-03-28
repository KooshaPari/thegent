# reflection_event_log API Reference

> **Source**: `src/thegent/integrations/reflection_event_log.py`

Reflection decision event logging for sync operations.

# @trace WL-195

---

## ReflectionDecision

A decision made during reflection phase.

---

## ReflectionEventLog

Event log for reflection decisions.

### Methods

#### ReflectionEventLog.__init__

```python
__init__(self: Any, log_path: Any)
```

Initialize the event log.

**Parameters**:

- `log_path`: Path to the JSONL event log file.
Defaults to docs/reference/reflection_events.jsonl

---

#### ReflectionEventLog.log

```python
log(self: Any, decision: ReflectionDecision)
```

Log a reflection decision.

**Parameters**:

- `decision`: ReflectionDecision to log.

---

#### ReflectionEventLog.read_all

```python
read_all(self: Any)
```

Read all logged decisions.

**Returns**: List of all ReflectionDecision events.

---

#### ReflectionEventLog.read_by_type

```python
read_by_type(self: Any, decision_type: str)
```

Read decisions of a specific type.

**Parameters**:

- `decision_type`: Type filter ('apply', 'skip', 'conflict').

**Returns**: List of matching ReflectionDecision events.

---

#### ReflectionEventLog.read_since

```python
read_since(self: Any, dt: datetime)
```

Read decisions since a specific datetime.

**Parameters**:

- `dt`: Cutoff datetime. Events with timestamp >= dt.isoformat() are included.

**Returns**: List of matching ReflectionDecision events.

---

---

## log

```python
log(self: Any, decision: ReflectionDecision)
```

Log a reflection decision.

**Parameters**:

- `decision`: ReflectionDecision to log.

---

## read_all

```python
read_all(self: Any)
```

Read all logged decisions.

**Returns**: List of all ReflectionDecision events.

---

## read_by_type

```python
read_by_type(self: Any, decision_type: str)
```

Read decisions of a specific type.

**Parameters**:

- `decision_type`: Type filter ('apply', 'skip', 'conflict').

**Returns**: List of matching ReflectionDecision events.

---

## read_since

```python
read_since(self: Any, dt: datetime)
```

Read decisions since a specific datetime.

**Parameters**:

- `dt`: Cutoff datetime. Events with timestamp >= dt.isoformat() are included.

**Returns**: List of matching ReflectionDecision events.

---

