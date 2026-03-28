# session_status_cmds API Reference

> **Source**: `src/thegent/cli/commands/session_status_cmds.py`

Thegent CLI session commands domain - extracted from cli.py (WL-124).

---

## inspect_cmd

```python
inspect_cmd(session_ids: Any, owner: Any, tail: int, stderr: bool, format: Any, include_contract: bool)
```

Show status and logs for one or more sessions. No shell loop needed.

---

## logs_cmd

```python
logs_cmd(session_id: Any, follow: bool, stderr: bool, tail: int, timeout: int, harness: bool) -> None
```

---

## status_cmd

```python
status_cmd(session_id: Any, format: Any, include_contract: bool) -> None
```

---

