# backlog API Reference

> **Source**: `src/thegent/governance/backlog.py`

Persistent backlog management for AgilePlus cycles.

Maintains a JSONL queue of known issues that could not be resolved in a single
cycle, enabling carry-over across cycles and audit trail of all findings.

---

## BacklogItem

A single backlog entry tracked across AgilePlus cycles.

**Inherits from**: `BaseModel`

---

## BacklogManager

Manages a persistent JSONL backlog of unresolved findings.

Items persist across AgilePlus cycles. Resolved items remain in the file
for audit trail but are excluded from get_pending() results.

### Methods

#### BacklogManager.__init__

```python
__init__(self, session_dir)
```

#### BacklogManager.add

Add a finding to the backlog as a new pending item.

```python
add(self, finding_id, dimension, severity, description)
```

#### BacklogManager.backlog_path

```python
backlog_path(self)
```

#### BacklogManager.defer

Mark a backlog item as deferred with a reason.

```python
defer(self, item_id, reason)
```

#### BacklogManager.get_all

Return all backlog items (including resolved/deferred) for audit trail.

```python
get_all(self)
```

#### BacklogManager.get_pending

Return pending items sorted by severity descending, then attempts ascending.

```python
get_pending(self)
```

#### BacklogManager.increment_attempt

Increment the attempt counter and update the last_attempted_at timestamp.

```python
increment_attempt(self, item_id)
```

#### BacklogManager.resolve

Mark a backlog item as resolved.

```python
resolve(self, item_id)
```

#### BacklogManager.update_status

Update the status of a backlog item.

```python
update_status(self, item_id, status, reason)
```

---

## BacklogStatus

Lifecycle status for backlog items.

**Inherits from**: `str, Enum`

---

## add

Add a finding to the backlog as a new pending item.

```python
add(self, finding_id, dimension, severity, description)
```

---

## backlog_path

```python
backlog_path(self)
```

---

## defer

Mark a backlog item as deferred with a reason.

```python
defer(self, item_id, reason)
```

---

## get_all

Return all backlog items (including resolved/deferred) for audit trail.

```python
get_all(self)
```

---

## get_pending

Return pending items sorted by severity descending, then attempts ascending.

```python
get_pending(self)
```

---

## increment_attempt

Increment the attempt counter and update the last_attempted_at timestamp.

```python
increment_attempt(self, item_id)
```

---

## resolve

Mark a backlog item as resolved.

```python
resolve(self, item_id)
```

---

## update_status

Update the status of a backlog item.

```python
update_status(self, item_id, status, reason)
```

---

