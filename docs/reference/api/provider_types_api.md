# provider_types API Reference

> **Source**: `src/thegent/routing/provider_types.py`

Provider type classification for execution path routing.

---

## ExecutionPath

Execution path for LLM provider.

**Inherits from**: `Enum`

---

## get_execution_path

Determine execution path for a provider.

Args:
    provider: Provider name (e.g., "codex", "minimax", "antigravity")

Returns:
    ExecutionPath enum value

```python
get_execution_path(provider)
```

---

