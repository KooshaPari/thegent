# orchestrate API Reference

> **Source**: `src/thegent/cli/apps/orchestrate.py`

Logical stream: Sub-agent orchestration commands.

Provides CLI commands for decomposing and executing goals via the
LLMPlangentPlanner -> PlangentExecutor -> SubAgentDispatcher pipeline.

# @trace FR-ORC-088
# @trace WL-088

---

## plan_cmd

```python
plan_cmd(goal: str, max_depth: int, model: str, timeout: float, json_output: bool)
```

Decompose *goal* into an OrchestrationPlan DAG and display the node table.

Uses LLMPlangentPlanner to call the model and produce a structured
decomposition.  Falls back to heuristic decomposition when the model
is unavailable (logged at WARNING level).

# @trace FR-ORC-088
# @trace WL-088

---

## run_cmd

```python
run_cmd(goal: str, max_depth: int, model: str, timeout: float, fail_fast: bool, json_output: bool)
```

Decompose *goal* and execute via PlangentExecutor, streaming SubAgentEvents.

Each dispatched node emits STARTED and COMPLETED events to the local
SubAgentEventQueue which are printed to stdout as they are drained.

Exit code 1 when any node fails.

# @trace FR-ORC-088
# @trace WL-088

---

