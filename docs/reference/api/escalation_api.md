# escalation API Reference

> **Source**: `src/thegent/governance/escalation.py`

WP-3008: Escalation SLA and governance queue (FR-028).

---

## EscalationItem

An item in the escalation queue.

### Methods

#### EscalationItem.from_dict

Create from dictionary.

```python
from_dict(cls, data)
```

#### EscalationItem.to_dict

Convert to dictionary for serialization.

```python
to_dict(self)
```

---

## EscalationPriority

Priority of an escalation item.

**Inherits from**: `str, Enum`

---

## EscalationQueue

Manages the governance escalation queue.

### Methods

#### EscalationQueue.__init__

```python
__init__(self, settings)
```

#### EscalationQueue.add

Simplified add for legacy/internal callers.

```python
add(self, run_id, reason, priority)
```

#### EscalationQueue.escalate

Add a new item to the escalation queue.

```python
escalate(self, run_id, prompt, reason, agent, priority, sla_minutes, metadata)
```

#### EscalationQueue.get_item

Retrieve a specific escalation item.

```python
get_item(self, esc_id)
```

#### EscalationQueue.list_items

List items in the queue, optionally filtered by status.

```python
list_items(self, status)
```

#### EscalationQueue.resolve

Mark an escalation item as resolved.

```python
resolve(self, esc_id, resolution, solver)
```

---

## EscalationStatus

Status of an escalation item.

**Inherits from**: `str, Enum`

---

## add

Simplified add for legacy/internal callers.

```python
add(self, run_id, reason, priority)
```

---

## escalate

Add a new item to the escalation queue.

```python
escalate(self, run_id, prompt, reason, agent, priority, sla_minutes, metadata)
```

---

## from_dict

Create from dictionary.

```python
from_dict(cls, data)
```

---

## get_item

Retrieve a specific escalation item.

```python
get_item(self, esc_id)
```

---

## list_items

List items in the queue, optionally filtered by status.

```python
list_items(self, status)
```

---

## resolve

Mark an escalation item as resolved.

```python
resolve(self, esc_id, resolution, solver)
```

---

## to_dict

Convert to dictionary for serialization.

```python
to_dict(self)
```

---

