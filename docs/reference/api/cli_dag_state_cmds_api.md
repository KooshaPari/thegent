# cli_dag_state_cmds API Reference

> **Source**: `src/thegent/cli/commands/cli_dag_state_cmds.py`

DAG CLI run, sync, recover, checkpoint commands (WL-120).

Advanced DAG operations: execution, synchronization, recovery, checkpointing.

---

## dag_cancel_cmd

```python
dag_cancel_cmd(task_id: str, cd: Any)
```

Cancel a task (set status to cancelled).

---

## dag_ready_cmd

```python
dag_ready_cmd(cd: Any, format: Any)
```

List task ids that are ready (pending with all deps done|cancelled|skipped).

---

## dag_status_cmd

```python
dag_status_cmd(cd: Any, format: Any)
```

For each task with session_id show id, status, session_id, session_status (running/exited:rc).

---

## dag_update_cmd

```python
dag_update_cmd(task_id: str, cd: Any, status: Any, session_id: Any, prompt: Any, agent: Any, depends_on: Any, contract_version: Any)
```

Update a task in the DAG. XA4: contract_version in task metadata.

---

