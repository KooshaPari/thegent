# types API Reference

> **Source**: `src/thegent/task/types.py`

Pydantic models for task types.

---

## Complexity

Task complexity level.

**Inherits from**: `str, Enum`

---

## Deliverable

A deliverable artifact.

**Inherits from**: `BaseModel`

---

## Priority

Priority level enumeration.

**Inherits from**: `str, Enum`

---

## SubagentType

Subagent type enumeration.

**Inherits from**: `str, Enum`

---

## Task

Task input model.

**Inherits from**: `BaseModel`

### Methods

#### Task.validate_allowed_agents

Validate allowed_agents is set when visibility is restricted.

```python
validate_allowed_agents(cls, v, info)
```

#### Task.validate_depends

Validate dependency IDs.

```python
validate_depends(cls, v)
```

---

## TaskMetadata

Task metadata.

**Inherits from**: `BaseModel`

---

## TaskOutput

Task execution output.

**Inherits from**: `BaseModel`

---

## TaskOutputStatus

Task output status.

**Inherits from**: `str, Enum`

---

## TaskStep

A single step in a task.

**Inherits from**: `BaseModel`

---

## TaskVisibility

Task visibility level.

**Inherits from**: `str, Enum`

---

## validate_allowed_agents

Validate allowed_agents is set when visibility is restricted.

```python
validate_allowed_agents(cls, v, info)
```

---

## validate_depends

Validate dependency IDs.

```python
validate_depends(cls, v)
```

---

