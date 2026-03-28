# impl_core API Reference

> **Source**: `src/thegent/cli/commands/impl_core.py`

Thegent core run/bg/resume/loop implementation layer.

---

## bg_impl

---

## loop_impl

```python
loop_impl(agent: str, prompt: str, todo_spec: str, checker: str, mode: str, cd: Any, on_worker_output: Any, on_progress: Any) -> dict[(str, Any)]
```

---

## resume_impl

```python
resume_impl(session_id: Any, prompt: Any, skills: Any) -> dict[(str, Any)]
```

---

## run_impl

```python
run_impl(agent: Any, prompt: str, cd: Any, mode: str, timeout: Any, full: bool, live: bool, model: Any, provider: Any, run_id: Any, owner: Any, include_contract: bool, route_contract: Any, route_request: Any, lane: str, confidence: Any, override_reason: Any, contract_version: Any, domain: Any, idempotency_token: Any, correlation_id: Any, speculative: bool, arbitration: Any, routing: Any, enable_search: bool, debug: bool, task_id: Any, shadow: bool, lock: Any, remote: Any, config_provider: Any, tenant_id: Any, previous_session_id: Any, reasoning_effort: Any, output_schema: Any, image_paths: Any, audio_files: Any, google_grounding: bool) -> dict[(str, Any)]
```

---

## session_send_impl

```python
session_send_impl(session_id: str, message: str, msg_type: str) -> tuple[(bool, str)]
```

---

