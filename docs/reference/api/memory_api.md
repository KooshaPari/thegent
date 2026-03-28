# memory API Reference

> **Source**: `src/thegent/cli/apps/memory.py`

Memory management CLI commands.

# @trace WL-060

---

## memory_dump_categories

```python
memory_dump_categories(project: Any, format: Any) -> None
```

---

## memory_dump_index

```python
memory_dump_index(project: Any, format: Any) -> None
```

---

## memory_dump_latest

```python
memory_dump_latest(project: Any, category: Any, json_only: bool, format: Any) -> None
```

---

## memory_garden

```python
memory_garden(dry_run: bool, max_age_days: int, project_root: str)
```

Run a full Gardener Agent cycle.

Reads memory logs, conversation dumps, and governance events;
detects stale documentation; synthesises rule-based updates; and
writes patches back to the relevant docs (unless --dry-run).

# @trace WL-060

---

## memory_snapshot_daily_export

```python
memory_snapshot_daily_export(project: Any, out_dir: Any, limit: int, trigger: Any, tag: Any, since: Any, format: Any) -> None
```

---

## memory_snapshot_daily_index

```python
memory_snapshot_daily_index(project: Any, limit: int, trigger: Any, tag: Any, since: Any, format: Any) -> None
```

---

## memory_snapshot_daily_totals

```python
memory_snapshot_daily_totals(project: Any, limit: int, trigger: Any, tag: Any, since: Any, format: Any) -> None
```

---

## memory_snapshot_export

```python
memory_snapshot_export(snapshot_path: Path, project: Any, out_path: Any, format: Any) -> None
```

---

## memory_snapshot_index

```python
memory_snapshot_index(project: Any, limit: int, format: Any) -> None
```

---

## memory_snapshot_list

```python
memory_snapshot_list(project: Any, limit: int, trigger: Any, tag: Any, since: Any, format: Any) -> None
```

---

## memory_snapshot_meta

```python
memory_snapshot_meta(project: Any, limit: int, format: Any) -> None
```

---

## memory_snapshot_prune

```python
memory_snapshot_prune(project: Any, max_keep: int, format: Any) -> None
```

---

