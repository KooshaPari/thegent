# dag_impl_ops API Reference

> **Source**: `src/thegent/cli/commands/dag_impl_ops.py`

DAG operations: list, ready, run, sync, recover (WL-120).

High-level DAG session operations (impl functions).

---

## dag_list_impl

```python
dag_list_impl(cd: Any)
```

List DAG tasks. Returns {frontmatter, tasks} or error.

---

## dag_raw_impl

```python
dag_raw_impl(cd: Any)
```

Get raw DAG markdown content. Returns markdown string or error message.

---

## dag_ready_impl

```python
dag_ready_impl(cd: Any)
```

List task ids that are ready (pending with all deps done|cancelled|skipped).

---

## dag_recover_impl

```python
dag_recover_impl(cd: Any, action: str)
```

Perform recovery playbook actions on the DAG.

---

## dag_run_impl

```python
dag_run_impl(cd: Any, dry_run: bool, task: Any, max_parallel: Any, lane: Any, check_drift: bool, contract_version: Any)
```

Spawn thegent bg for each ready task; update status=running and session_id.

---

## dag_status_impl

```python
dag_status_impl(cd: Any)
```

For each task with session_id show id, status, session_id, session_status.

---

## dag_sync_impl

```python
dag_sync_impl(cd: Any, auto_run_next: bool)
```

For tasks with session_id and status=running, if pid not running set status=done or failed from rc.

---

## rules_sync_impl

```python
rules_sync_impl(cd: Any, force: bool, check: bool)
```

Sync rules implementation (WP-9002).

---

