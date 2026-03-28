# dex_utility_cmds API Reference

> **Source**: `src/thegent/dex_utility_cmds.py`

Utility commands for dex CLI.

Session management and utility commands.
Extracted from dex_main.py for maintainability.

---

## dex_config

```python
dex_config(key: Any, value: Any)
```

View or edit dex configuration.

---

## dex_doctor

Run dex diagnostics.

---

## dex_fork

```python
dex_fork(session_id: str)
```

Fork a dex session.

---

## dex_history

```python
dex_history(limit: int)
```

Show dex session history.

---

## dex_inspect

```python
dex_inspect(session_id: str)
```

Inspect a dex session in detail.

---

## dex_logs

```python
dex_logs(session_id: str, follow: bool)
```

View logs for a dex session.

---

## dex_ps

List running dex sessions.

---

## dex_resume

```python
dex_resume(session_id: str)
```

Resume a paused dex session.

---

## dex_status

```python
dex_status(session_id: Any)
```

Show status of dex sessions.

---

## dex_stop

```python
dex_stop(session_id: str, force: bool)
```

Stop a running dex session.

---

## dex_wait

```python
dex_wait(session_id: str)
```

Wait for a dex session to complete.

---

## register_dex_utility_commands

```python
register_dex_utility_commands(app: typer.Typer)
```

Register utility commands with the app.

**Parameters**:

- `app`: Typer app to register commands with

---

