# modes API Reference

> **Source**: `src/thegent/agents/modes.py`

Multi-agent execution modes and selection policy.

Defines coordination patterns for multi-agent workflows (FR-032).

---

## ExecutionMode

Coordination patterns for multi-agent execution.

**Inherits from**: `StrEnum`

---

## ModeCapability

Metadata for an execution mode.

**Inherits from**: `BaseModel`

---

## get_mode_capability

```python
get_mode_capability(mode: str)
```

Get capability metadata for a mode string.

---

## list_modes

List all available execution modes.

---

