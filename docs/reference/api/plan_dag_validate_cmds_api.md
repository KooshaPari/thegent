# plan_dag_validate_cmds API Reference

> **Source**: `src/thegent/cli/plan/plan_dag_validate_cmds.py`

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

## dag_list_cmd

```python
dag_list_cmd(cd: Any, format: Any)
```

Parse and display DAG session from .factory/dag-session.md.

---

## dag_remove_cmd

```python
dag_remove_cmd(task_id: str, cd: Any)
```

Remove a task from the DAG.

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

## dag_validate_cmd

```python
dag_validate_cmd(cd: Any)
```

Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.

---

