# harness API Reference

> **Source**: `src/thegent/crew/harness.py`

Integration with thegent codex/cc/droid harness.

---

## agent_executor

```python
agent_executor(agent_id: str, prompt: str, context: dict[(str, Any)])
```

Execute agent via thegent harness.

**Parameters**:

- `agent_id`: Agent identifier (e.g., "codex", "cursor-agent", "claude", "copilot", "gemini", "droid")
- `prompt`: Task prompt
- `context`: Execution context

**Returns**: ExecutionResult

---

## create_agent_executor

```python
create_agent_executor(cwd: Any, mode: str, timeout: int, model: Any, agent_map: Any)
```

Create agent_executor callback that uses thegent's codex/cc/droid harness.

**Parameters**:

- `cwd`: Working directory for agent execution
- `mode`: Execution mode (read-only, write, full)
- `timeout`: Timeout in seconds
- `model`: Optional model override
- `agent_map`: Optional map of agent_id -> agent_name/role

**Returns**: Callable (agent_id, prompt, context) -> ExecutionResult

---

