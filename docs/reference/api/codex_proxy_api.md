# codex_proxy API Reference

> **Source**: `src/thegent/agents/codex_proxy.py`

Codex via CLIProxyAPIPlus - claude, codex, gemini, copilot, antigravity through our proxy. Native gemini/copilot swapped to Codex (proxy API).

---

## CodexProxyRunner

Runs claude, codex, gemini, copilot, antigravity via Codex CLI pointing at our CLIProxyAPIPlus. gemini/copilot route via proxy (no native CLI).

**Inherits from**: `AgentRunner`

### Methods

#### CodexProxyRunner.__init__

```python
__init__(self, agent_name, settings, model)
```

#### CodexProxyRunner.run

```python
run(self, prompt, cwd, mode, timeout)
```

#### CodexProxyRunner.run_with_metadata

Run agent using resolved routing from TaskMetadata.

This method consumes resolved_provider and resolved_model_alias
from the routing classification.

Args:
    prompt: User prompt
    cwd: Working directory
    mode: Execution mode (read/write/full)
    timeout: Timeout in seconds
    metadata: TaskMetadata with resolved routing

Returns:
    RunResult from execution

```python
run_with_metadata(self, prompt, cwd, mode, timeout)
```

---

## run

```python
run(self, prompt, cwd, mode, timeout)
```

---

## run_with_metadata

Run agent using resolved routing from TaskMetadata.

This method consumes resolved_provider and resolved_model_alias
from the routing classification.

Args:
    prompt: User prompt
    cwd: Working directory
    mode: Execution mode (read/write/full)
    timeout: Timeout in seconds
    metadata: TaskMetadata with resolved routing

Returns:
    RunResult from execution

```python
run_with_metadata(self, prompt, cwd, mode, timeout)
```

---

