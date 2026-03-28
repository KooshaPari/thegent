# plan_output_helpers API Reference

> **Source**: `src/thegent/cli/plan/plan_output_helpers.py`

Rendering helpers for plan/DAG CLI commands.

---

## render_dag_list

```python
render_dag_list(tasks: list[dict[(str, str)]], fmt: str)
```

Render `dag list` output for json/md/rich formats.

---

## render_dag_ready

```python
render_dag_ready(ready_ids: list[str], tasks: list[dict[(str, str)]], fmt: str)
```

Render `dag ready` output for ids/json/md/rich formats.

---

## render_dag_status

```python
render_dag_status(rows: list[dict[(str, str)]], fmt: str)
```

Render `dag status` output for json/md/rich formats.

---

## render_plan_next_items

```python
render_plan_next_items(items: list[dict[(str, str)]])
```

Render `plan do-next` items in rich table format.

---

## resolve_output_format

```python
resolve_output_format(requested: Any, settings: Any)
```

Normalize command output format using CLI settings fallback.

---

