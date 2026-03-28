# infra_impl API Reference

> **Source**: `src/thegent/cli/commands/infra_impl.py`

Infra/compute/sandbox/concurrency/orchestration backend logic (WL-120 W3-B3).

---

## concurrency_set_impl

```python
concurrency_set_impl(limit: int, load_based: bool)
```

Set maximum concurrency limit (env-var based; prints persistence instructions).

---

## concurrency_show_impl

Show current concurrency limits and load-based status.

---

## generate_monitor_layout

---

## isolation_check_impl

```python
isolation_check_impl(mode: str)
```

Implementation of 'thegent isolation check'.

---

## lock_resource_impl

```python
lock_resource_impl(resource_path: str, agent_id: str, ttl: int, cd: Any)
```

Claim a lease on a resource (file or directory).

---

## monitor_impl

```python
monitor_impl(interval: float)
```

Monitor sessions and plan progress in real-time (WP-8001).

---

## orchestrate_plan_impl

```python
orchestrate_plan_impl(goal: str)
```

Decompose *goal* into an OrchestrationPlan dict via LLMPlangentPlanner. # @trace FR-ORC-088

---

## orchestrate_run_impl

```python
orchestrate_run_impl(goal: str)
```

Decompose *goal* and execute via PlangentExecutor + SubAgentDispatcher. # @trace FR-ORC-088

---

## unlock_resource_impl

```python
unlock_resource_impl(resource_path: str, agent_id: str, token: str, cd: Any)
```

Release a lease on a resource.

---

## verify_context_impl

```python
verify_context_impl(files: list[str], cd: Any)
```

Verify if any of the given files have been modified (OCC check).

---

