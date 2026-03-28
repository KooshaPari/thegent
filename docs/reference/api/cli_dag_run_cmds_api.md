# cli_dag_run_cmds API Reference

> **Source**: `src/thegent/cli/commands/run/cli_dag_run_cmds.py`

DAG CLI run, sync, recover, checkpoint commands (WL-120).

Advanced DAG operations: execution, synchronization, recovery, checkpointing.

---

## dag_reconcile_cmd

```python
dag_reconcile_cmd(cd: Any)
```

Reconcile DAG state with reality (clean up stuck 'running' tasks).

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

---

