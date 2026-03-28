# run_dag_helpers API Reference

> **Source**: `src/thegent/cli/services/run_dag_helpers.py`

DAG helper service wrappers for impl.py compatibility.

---

## dag_ready_impl

```python
dag_ready_impl(cd: Any) -> dict[(str, Any)]
```

---

## dag_update_task

```python
dag_update_task(doc: DagDocument, task_id: str) -> bool
```

---

## get_ready_task_ids

```python
get_ready_task_ids(tasks: list[dict[(str, str)]]) -> list[str]
```

---

## parse_dag_full

```python
parse_dag_full(path: Path) -> DagDocument
```

---

## parse_dag_session

```python
parse_dag_session(path: Path) -> tuple[(dict[(str, str)], list[dict[(str, str)]])]
```

---

## parse_depends_on

```python
parse_depends_on(dep_str: str) -> list[str]
```

---

## serialize_dag

```python
serialize_dag(doc: DagDocument) -> str
```

---

## validate_agent

```python
validate_agent(agent: str) -> Any
```

---

## validate_dag

```python
validate_dag(doc: DagDocument) -> list[str]
```

---

## validate_task_id

```python
validate_task_id(task_id: str) -> Any
```

---

