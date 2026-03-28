# codex_proxy API Reference

> **Source**: `src/thegent/agents/codex_proxy.py`

Codex via CLIProxyAPIPlus - multi-agent support.

Runs claude, codex, gemini, copilot, antigravity through CLIProxyAPIPlus.
Native gemini/copilot swapped to Codex (proxy API).

---

## CodexAuthError

Raised on authentication failures.

**Inherits from**: `Exception`

---

## CodexInstanceError

Raised when concurrent instance limit exceeded.

**Inherits from**: `Exception`

---

## CodexModelError

Raised on model-specific errors.

**Inherits from**: `Exception`

---

## CodexProxyAdapter

Codex proxy adapter for agent execution

### Methods

#### CodexProxyAdapter.__init__

```python
__init__(self: Any)
```

---

#### CodexProxyAdapter.call

```python
call(self: Any)
```

Execute via Codex proxy

---

---

## CodexProxyRunner

Runs agents via Codex CLI pointing at CLIProxyAPIPlus.

Supports multi-agent on-device workflows with:
- Instance isolation via CODEX_HOME (isolated SQLite state)
- Resource-aware spawning with max_concurrent limits
- Structured JSONL output parsing (tokens, model, cost)
- Config injection via temporary config.toml files
- Typed error handling (AuthError, SandboxError, etc.)

**Inherits from**: `AgentRunner`

### Methods

#### CodexProxyRunner.__init__

```python
__init__(self: Any, agent_name: str, settings: Any, model: str, use_litellm_router: Any, codex_home: Any, memory_limit_mb: int, max_concurrent_instances: int, config_overrides: Any, keep_isolated_home: bool)
```

---

#### CodexProxyRunner.run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

---

#### CodexProxyRunner.run_lightweight

```python
run_lightweight(self: Any, prompt: str, cwd: Any, timeout: int)
```

Run Codex in lightweight mode optimized for multi-agent orchestration.

Automatically isolates state, uses workspace-write sandbox, and enables JSON streaming.
Suitable for running 5-10 concurrent instances on a single machine.

**Parameters**:

- `prompt`: User task/prompt
- `cwd`: Working directory
- `timeout`: Timeout in seconds (default 10 min for lightweight tasks)
- `agent_index`: Unique agent ID (0-9 for pool of 10) for state isolation
- `use_stream`: Whether to use JSON streaming (default True)
- `live_output`: Callback-based live output (default False)
- `on_stdout`: Callback for stdout lines
- `on_stderr`: Callback for stderr lines
- `agent_model`: Override default model
- `config`: Additional Codex config overrides (dict of key=value)
- `env`: Additional environment variables

**Returns**: RunResult with exit code, stdout, stderr, timed_out flag

---

#### CodexProxyRunner.run_with_metadata

```python
run_with_metadata(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

Run agent using resolved routing from TaskMetadata.

This method consumes resolved_provider and resolved_model_alias
from the routing classification.

**Parameters**:

- `prompt`: User prompt
- `cwd`: Working directory
- `mode`: Execution mode (read/write/full)
- `timeout`: Timeout in seconds
- `metadata`: TaskMetadata with resolved routing

**Returns**: RunResult from execution

---

---

## CodexResult

Structured result from Codex execution with token usage and model info.

# @trace FR-AGT-001

---

## CodexSandboxError

Raised on sandbox/permission errors.

**Inherits from**: `Exception`

---

## call

```python
call(self: Any)
```

Execute via Codex proxy

---

## run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int) -> RunResult
```

---

## run_lightweight

```python
run_lightweight(self: Any, prompt: str, cwd: Any, timeout: int)
```

Run Codex in lightweight mode optimized for multi-agent orchestration.

Automatically isolates state, uses workspace-write sandbox, and enables JSON streaming.
Suitable for running 5-10 concurrent instances on a single machine.

**Parameters**:

- `prompt`: User task/prompt
- `cwd`: Working directory
- `timeout`: Timeout in seconds (default 10 min for lightweight tasks)
- `agent_index`: Unique agent ID (0-9 for pool of 10) for state isolation
- `use_stream`: Whether to use JSON streaming (default True)
- `live_output`: Callback-based live output (default False)
- `on_stdout`: Callback for stdout lines
- `on_stderr`: Callback for stderr lines
- `agent_model`: Override default model
- `config`: Additional Codex config overrides (dict of key=value)
- `env`: Additional environment variables

**Returns**: RunResult with exit code, stdout, stderr, timed_out flag

---

## run_with_metadata

```python
run_with_metadata(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

Run agent using resolved routing from TaskMetadata.

This method consumes resolved_provider and resolved_model_alias
from the routing classification.

**Parameters**:

- `prompt`: User prompt
- `cwd`: Working directory
- `mode`: Execution mode (read/write/full)
- `timeout`: Timeout in seconds
- `metadata`: TaskMetadata with resolved routing

**Returns**: RunResult from execution

---

