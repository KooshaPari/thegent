# plan_dag_sync_recover_cmds API Reference

> **Source**: `src/thegent/cli/plan/plan_dag_sync_recover_cmds.py`

Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

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

## dag_probe_cmd

```python
dag_probe_cmd(cd: Any, baseline_id: Any)
```

Compare current DAG state with a baseline checkpoint to detect regressions.

---

## dag_recover_cmd

```python
dag_recover_cmd(cd: Any, action: str)
```

Perform recovery playbook actions on the DAG.

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

## dag_sync_cmd

```python
dag_sync_cmd(cd: Any, auto_run_next: bool)
```

For tasks with session_id and status=running, if pid not running set status=done or failed from rc.

If --auto-run-next, spawn next ready tasks after sync.

---

