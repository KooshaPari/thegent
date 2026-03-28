# plan_dag_cmds API Reference

> **Source**: `src/thegent/cli/plan/plan_dag_cmds.py`

Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

---

## dag_add_cmd

```python
dag_add_cmd(task_id: str, agent: str, prompt: str, cd: Any, depends_on: Any, contract_version: Any)
```

Add a task to the DAG. XA4: contract_version in task metadata.

---

## dag_cancel_cmd

```python
dag_cancel_cmd(task_id: str, cd: Any)
```

Cancel a task (set status to cancelled).

---

## dag_checkpoint_cmd

```python
dag_checkpoint_cmd(cd: Any, reason: str)
```

Create a point-in-time checkpoint of the DAG state.

---

## dag_checkpoints_cmd

```python
dag_checkpoints_cmd(limit: int)
```

List recent DAG checkpoints.

---

## dag_list_cmd

```python
dag_list_cmd(cd: Any, format: Any)
```

Parse and display DAG session from .factory/dag-session.md.

---

## dag_probe_cmd

```python
dag_probe_cmd(cd: Any, baseline_id: Any)
```

Compare current DAG state with a baseline checkpoint to detect regressions.

---

## dag_ready_cmd

```python
dag_ready_cmd(cd: Any, format: Any)
```

List task ids that are ready (pending with all deps done|cancelled|skipped).

---

## dag_reconcile_cmd

```python
dag_reconcile_cmd(cd: Any)
```

Reconcile DAG state with reality (clean up stuck 'running' tasks).

---

## dag_recover_cmd

```python
dag_recover_cmd(cd: Any, action: str)
```

Perform recovery playbook actions on the DAG.

---

## dag_remove_cmd

```python
dag_remove_cmd(task_id: str, cd: Any)
```

Remove a task from the DAG.

---

## dag_rollback_cmd

```python
dag_rollback_cmd(checkpoint_id: Any, cd: Any)
```

Rollback DAG state to a specific checkpoint.

---

## dag_run_cmd

```python
dag_run_cmd(cd: Any, dry_run: bool, task: Any, max_parallel: Any, lane: Any, check_drift: bool, contract_version: Any)
```

Spawn thegent bg for each ready task; update status=running and session_id.

---

## dag_status_cmd

```python
dag_status_cmd(cd: Any, format: Any)
```

For each task with session_id show id, status, session_id, session_status (running/exited:rc).

---

## dag_sync_cmd

```python
dag_sync_cmd(cd: Any, auto_run_next: bool)
```

For tasks with session_id and status=running, if pid not running set status=done or failed from rc.

If --auto-run-next, spawn next ready tasks after sync.

---

## dag_update_cmd

```python
dag_update_cmd(task_id: str, cd: Any, status: Any, session_id: Any, prompt: Any, agent: Any, depends_on: Any, contract_version: Any)
```

Update a task in the DAG. XA4: contract_version in task metadata.

---

## dag_validate_cmd

```python
dag_validate_cmd(cd: Any)
```

Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.

---

