# run_cmds API Reference

> **Source**: `src/thegent/cli/commands/run/run_cmds.py`

Thegent CLI run commands domain - facade with re-exports (WL-124).

---

## bg_cmd

```python
bg_cmd(agent: Any, prompt: str, cd: Any, name: Any, model: Any, provider: Any, timeout: int, lane: str, confidence: Any, domain: Any, task_id: Any, image: Any, audio: Any, skills: Any)
```

Background run: spawn session and return immediately with session ID.

---

## retry_cmd

```python
retry_cmd(run_id: str)
```

Retry a failed run with the same parameters.

---

## run_cmd

```python
run_cmd(agent: Any, prompt: str, cd: Any, mode: str, timeout: int, full: bool, live: bool, model: Any, provider: Any, failover: bool, routing: Any, include_contract: bool, run_id: Any, lane: str, idempotency_token: Any, confidence: Any, arbitration: Any, override_reason: Any, contract_version: Any, domain: Any, speculative: bool, search: bool, debug: bool, task_id: Any, shadow: bool, lock: Any, remote: Any, output_schema: Any, image: Any, audio: Any, google_grounding: bool, reasoning: Any, skills: Any)
```

Run an agent or droid with the given prompt. Model-first: agent=None, model set.

---

