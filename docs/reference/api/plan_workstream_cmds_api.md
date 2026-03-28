# plan_workstream_cmds API Reference

> **Source**: `src/thegent/cli/plan/plan_workstream_cmds.py`

Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

---

## closure_pack_cmd

```python
closure_pack_cmd(cd: Any)
```

Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024).

---

## plan_analyze_cmd

```python
plan_analyze_cmd(cd: Any, pert: bool, resources: bool, continuity: bool, format: Any)
```

Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.

---

## plan_claim_cmd

```python
plan_claim_cmd(item_id: str, agent_id: Any, cd: Any)
```

Claim an item in the unified work stream.

---

## plan_complete_cmd

```python
plan_complete_cmd(item_id: str, agent_id: Any, cd: Any)
```

Mark an item as complete in the unified work stream.

---

## plan_do_next_cmd

```python
plan_do_next_cmd(cd: Any, limit: int, format: Any)
```

Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

---

## plan_get_next_cmd

```python
plan_get_next_cmd(cd: Any, format: Any)
```

Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)

---

## plan_incorporate_cmd

```python
plan_incorporate_cmd(cd: Any, dry_run: bool)
```

Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.

---

## plan_lint_workstream_cmd

```python
plan_lint_workstream_cmd(cd: Any)
```

Validate canonical WORK_STREAM schema structure.

---

## plan_loop_cmd

```python
plan_loop_cmd(cd: Any, max_iterations: int, sleep_seconds: float, agent: str, dry_run: bool)
```

Loop: get next item -> run bg -> repeat until no items or --max reached.

---

## plan_normalize_workstream_cmd

```python
plan_normalize_workstream_cmd(cd: Any)
```

Sort and normalize WL sections and status-line formatting.

---

## plan_progress_cmd

```python
plan_progress_cmd(limit: int, format: Any)
```

Show recent runs (work-package progress). Alias for history --limit N.

---

## plan_verify_workstream_cmd

```python
plan_verify_workstream_cmd(cd: Any, format: Any)
```

Verify WORK_STREAM invariants for CLAIMED/COMPLETED overlap by exact ID match.

---

## plan_wait_next_cmd

```python
plan_wait_next_cmd(cd: Any, poll: float, timeout: float, sources: Any, format: Any)
```

Block until next actionable work exists (DAG ready, do_next, escalation, inbox).

---

## workstream_query_cmd

```python
workstream_query_cmd(query: str)
```

Execute SQL query on workstream database.

---

