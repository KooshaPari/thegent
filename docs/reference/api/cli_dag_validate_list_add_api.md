# cli_dag_validate_list_add API Reference

> **Source**: `src/thegent/cli/commands/cli_dag_validate_list_add.py`

DAG CLI validate, list, add, remove commands (WL-120).

Basic DAG manipulation: validation, listing, adding/removing tasks.

---

## dag_add_cmd

```python
dag_add_cmd(task_id: str, agent: str, prompt: str, cd: Any, depends_on: Any, contract_version: Any)
```

Add a task to the DAG. XA4: contract_version in task metadata.

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

## dag_validate_cmd

```python
dag_validate_cmd(cd: Any)
```

Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.

---

