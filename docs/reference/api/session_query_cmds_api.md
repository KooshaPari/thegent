# session_query_cmds API Reference

> **Source**: `src/thegent/cli/commands/session_query_cmds.py`

Thegent CLI session query commands (from session_cmds.py).

---

## events_cmd

```python
events_cmd(run_id: Any, limit: int, format: Any)
```

List raw telemetry events.

---

## feedback_cmd

```python
feedback_cmd(run_id: Any, score: float, note: Any)
```

Provide operator feedback for a specific run.

---

## history_cmd

```python
history_cmd(limit: int, format: Any)
```

List execution run history (sync and background).

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

## ps_cmd

```python
ps_cmd(all_sessions: bool, owner: Any, format: Any, include_contract: bool) -> None
```

---

## status_cmd

```python
status_cmd(session_id: Any, format: Any, include_contract: bool) -> None
```

---

