# execute_task API Reference

> **Source**: `src/thegent/use_cases/execute_task.py`

Pure execution orchestration logic (no I/O, no subprocess).

This module contains the core business logic for task execution orchestration,
separated from I/O and subprocess management. Coordinates:
- Agent/model resolution
- Budget checking
- Routing decisions
- Policy evaluation
- Concurrency control
- Registry integration
- Error classification

---

## ExecutionOrchestrator

Orchestrates agent execution without I/O operations.

### Methods

#### ExecutionOrchestrator.build_run_metadata

```python
build_run_metadata(run_id: str, agent: str, model: Any, prompt: str, cwd: Path, mode: str, owner: str)
```

Build run metadata dict for registry and auditing.

Additional kwargs are merged into the metadata.

---

#### ExecutionOrchestrator.check_idempotency

```python
check_idempotency(idempotency_token: Any, registry: Any)
```

Check for existing run via idempotency token.

Returns dict with cached result if replay detected, None otherwise.

---

#### ExecutionOrchestrator.classify_error

```python
classify_error(result: Any)
```

Classify error from agent result.

Returns error_class string or None if no error.

---

#### ExecutionOrchestrator.compute_agents_to_try

```python
compute_agents_to_try(primary_agent: str, model: Any)
```

Build fallback chain from primary agent and model routes.

---

#### ExecutionOrchestrator.record_execution_end

```python
record_execution_end(registry: Any, run_id: str, exit_code: int, status: str, error_class: Any, cost_usd: Any)
```

Record execution completion in registry.

---

#### ExecutionOrchestrator.validate_timeout

```python
validate_timeout(timeout: Any, agent: str, default: int)
```

Compute effective timeout with agent-specific minimums.

---

---

## build_run_metadata

```python
build_run_metadata(run_id: str, agent: str, model: Any, prompt: str, cwd: Path, mode: str, owner: str)
```

Build run metadata dict for registry and auditing.

Additional kwargs are merged into the metadata.

---

## check_idempotency

```python
check_idempotency(idempotency_token: Any, registry: Any)
```

Check for existing run via idempotency token.

Returns dict with cached result if replay detected, None otherwise.

---

## classify_error

```python
classify_error(result: Any)
```

Classify error from agent result.

Returns error_class string or None if no error.

---

## compute_agents_to_try

```python
compute_agents_to_try(primary_agent: str, model: Any)
```

Build fallback chain from primary agent and model routes.

---

## record_execution_end

```python
record_execution_end(registry: Any, run_id: str, exit_code: int, status: str, error_class: Any, cost_usd: Any)
```

Record execution completion in registry.

---

## validate_timeout

```python
validate_timeout(timeout: Any, agent: str, default: int)
```

Compute effective timeout with agent-specific minimums.

---

