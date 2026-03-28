# post_agent_run_hook API Reference

> **Source**: `src/thegent/governance/post_agent_run_hook.py`

PostAgentRun hook dispatcher wiring for agent and orchestration surfaces.

---

## dispatch_post_agent_run_hook

```python
dispatch_post_agent_run_hook(result: Any, run_id: Any, session_id: Any, cwd: Any, extra_context: Any)
```

Dispatch ``hook-dispatcher postagentrun`` and fail fast on execution errors.

---

