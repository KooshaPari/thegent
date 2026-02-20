# provider_types API Reference

> **Source**: `src/thegent/routing/provider_types.py`

Provider type classification for execution path routing.

---

## ExecutionPath

Execution path for LLM provider.

**Inherits from**: `Enum`

---

## get_execution_path

```python
get_execution_path(provider: str)
```

Determine execution path for a provider.

**Parameters**:

- `provider`: Provider name (e.g., "codex", "minimax", "antigravity")

**Returns**: ExecutionPath enum value

---

