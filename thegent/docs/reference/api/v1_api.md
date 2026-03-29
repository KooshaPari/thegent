# v1 API Reference

> **Source**: `src/thegent/contracts/csm/v1/__init__.py`

Canonical Structured Message (CSM) schema v1.

Unifies task-tool 18-tag and Zen rich protocol into a single typed schema
for orchestration events and agent outputs.

---

## CSMPhase

Canonical phase for multi-agent workflows (Planner/Operator/Reviewer).

**Inherits from**: `StrEnum`

---

## CSMStatus

Canonical status values for agent/output lifecycle.

**Inherits from**: `StrEnum`

---

## CanonicalStructuredMessage

Canonical schema for agent output normalization.

Maps task-tool 18-tag and Zen rich protocol into one typed structure.

### Methods

#### CanonicalStructuredMessage.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Deserialize from dict.

---

#### CanonicalStructuredMessage.to_dict

```python
to_dict(self: Any)
```

Serialize to dict for JSON/transport.

---

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Deserialize from dict.

---

## to_dict

```python
to_dict(self: Any)
```

Serialize to dict for JSON/transport.

---
