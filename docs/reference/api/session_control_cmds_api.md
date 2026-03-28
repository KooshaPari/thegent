# session_control_cmds API Reference

> **Source**: `src/thegent/cli/commands/session_control_cmds.py`

## deferral_list_cmd

List all currently deferred tasks (WP-5004).

---

## deferral_resume_cmd

```python
deferral_resume_cmd(run_id: str)
```

Manually resume a deferred task (WP-5004).

---

## pause_cmd

```python
pause_cmd(session_id: Any)
```

Pause a background session (register pause event).

---

## resume_cmd

```python
resume_cmd(session_id: Any, prompt: Any, skills: Any)
```

Resume a session in the registry state machine.

---

## session_cmd

```python
session_cmd(session_id: Any, watch: bool, action: Any)
```

Rich TUI for session management with subagent monitoring (WP-8002).

---

## session_fork_cmd

```python
session_fork_cmd(session_id: str, from_turn: Any, new_session_id: Any)
```

Fork a session via SessionManager API.

---

## session_rollback_cmd

```python
session_rollback_cmd(session_id: str, n_turns: int)
```

Rollback a session via SessionManager API.

---

## stop_cmd

```python
stop_cmd(session_id: Any, force: bool, wind_down: bool, grace: int) -> None
```

---

## wait_cmd

```python
wait_cmd(session_id: Any, timeout: int) -> None
```

---

