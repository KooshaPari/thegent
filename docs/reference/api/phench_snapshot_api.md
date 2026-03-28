# phench_snapshot API Reference

> **Source**: `src/thegent/cli/apps/phench_snapshot.py`

Phench snapshot commands.

---

## register_snapshot_commands

```python
register_snapshot_commands(snapshot_app: typer.Typer, create_target_snapshot_fn: Any, list_target_snapshots_fn: Any, show_target_snapshot_fn: Any)
```

Register snapshot commands on the phench snapshot sub-app.

---

## snapshot_create_cmd

```python
snapshot_create_cmd(target: str, family: Any, snapshot_id: Any) -> None
```

---

## snapshot_list_cmd

```python
snapshot_list_cmd(target: str, family: Any) -> None
```

---

## snapshot_show_cmd

```python
snapshot_show_cmd(target: str, family: Any, snapshot_id: str) -> None
```

---

