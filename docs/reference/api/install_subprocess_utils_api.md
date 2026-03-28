# install_subprocess_utils API Reference

> **Source**: `src/thegent/install_subprocess_utils.py`

Shared subprocess helpers for install workflows.

---

## command_exists

```python
command_exists(cmd: str)
```

Check if a command exists in PATH.

---

## run_command

```python
run_command(cmd: list[str], check: bool, capture_output: bool, retries: int, retry_delay: float)
```

Run a shell command with retry logic using tenacity.

Returns (returncode, stdout, stderr).

---

