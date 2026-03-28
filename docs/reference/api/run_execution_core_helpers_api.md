# run_execution_core_helpers API Reference

> **Source**: `src/thegent/cli/services/run_execution_core_helpers.py`

Extracted execution cores for run/bg commands.

DEPRECATED: This module is now a thin shim for backward compatibility.
New code should use the decomposed modules:
- thegent.use_cases.execute_task — Pure orchestration logic
- thegent.adapters.execution_io — I/O and subprocess management

These helpers accept an injected impl module namespace to preserve existing
runtime wiring while avoiding circular imports from impl.py.

---

## RunnerProxy

**Inherits from**: `AgentRunner`

### Methods

#### RunnerProxy.run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

---

---

## _LazyImpl

### Methods

---

## bg_impl_core

Start a background run. Returns dict with keys: session_id, log_path, owner.

---

## run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int) -> RunResult
```

---

## run_impl_core

```python
run_impl_core(agent: Any, prompt: str, cd: Any, mode: str, timeout: Any, full: bool, live: bool, model: Any, provider: Any, run_id: Any, owner: Any, include_contract: bool, route_contract: Any, route_request: Any, lane: str, confidence: Any, override_reason: Any, contract_version: Any, domain: Any, idempotency_token: Any, correlation_id: Any, speculative: bool, arbitration: Any, routing: Any, enable_search: bool, debug: bool, task_id: Any, shadow: bool, lock: Any, remote: Any, config_provider: ConfigProvider | None, tenant_id: Any, previous_session_id: Any, reasoning_effort: Any, output_schema: Any, image_paths: Any, audio_files: Any, google_grounding: bool, impl_ns: Any)
```

Run an agent or droid with the given prompt.

Returns dict with keys: stdout, stderr, exit_code, timed_out.
Model-first: agent=None, model set; provider hint for routing.

---

## runner_factory

```python
runner_factory(agent_name: str) -> Any
```

---

## wrapped_run

---

