# run_cmds_loop API Reference

> **Source**: `src/thegent/cli/commands/run/run_cmds_loop.py`

Thegent CLI run commands domain - extracted from cli.py (WL-124).

---

## loop_cmd

```python
loop_cmd(prompt: str, todo_spec: str, agent: Any, checker: str, loop_mode: str, cd: Any)
```

Run a Lifecycle loop with Checker oversight.

---

## loop_send_cmd

```python
loop_send_cmd(session_id: Any, prompt: str)
```

Send a prompt to a running Lifecycle loop (human or agent takeover).

---

## loop_stop_cmd

```python
loop_stop_cmd(session_id: Any)
```

Send STOP signal to a running Lifecycle loop.

---

## on_progress

```python
on_progress(iteration: int, total: int, message: str) -> None
```

---

## on_worker_output

```python
on_worker_output(text: str) -> None
```

---

