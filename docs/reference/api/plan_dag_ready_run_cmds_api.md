# plan_dag_ready_run_cmds API Reference

> **Source**: `src/thegent/cli/commands/run/plan_dag_ready_run_cmds.py`

Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

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

