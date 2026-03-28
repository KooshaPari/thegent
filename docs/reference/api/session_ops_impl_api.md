# session_ops_impl API Reference

> **Source**: `src/thegent/cli/commands/session_ops_impl.py`

Session inspection and log operations: status, inspect, logs.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
Listing operations (ps, session_list) extracted to session_ops_list_impl.py.
Contains:
- status_impl: get status of a background session
- inspect_impl: get status + logs for one or more sessions
- logs_impl: get or follow logs from a background session

---

## inspect_impl

```python
inspect_impl(session_ids: list[str], owner: Any, tail: int, stderr: bool, include_contract: bool)
```

Get status and logs for one or more sessions. Returns list of {session_id, status, logs}.

---

## logs_impl

```python
logs_impl(session_id: str, tail: Any, stderr: bool, follow: bool)
```

Get or follow logs from a background session. Returns log text or None if following.

---

## status_impl

```python
status_impl(session_id: str, include_contract: bool)
```

Get status of a background session.

---

