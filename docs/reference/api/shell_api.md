# shell API Reference

> **Source**: `src/thegent/utils/shell.py`

Shell optimization utilities.

Ensures all shell invocations use the fastest available shell (zsh > bash > sh).

---

## get_fastest_shell

Get fastest available shell.
Priority: zsh > bash > sh

Returns:
    Path to fastest available shell executable

---

## get_shell_env

Get optimized environment for shell execution.

Args:
    optimize_startup: If True, skip heavy .zshrc loading for non-interactive shells

Returns:
    Environment dict with optimizations

```python
get_shell_env(optimize_startup)
```

---

## popen_shell_command

Open shell process using fastest available shell.

Args:
    cmd: Command string or list to execute
    shell: Shell executable path (defaults to fastest available)
    optimize_startup: Skip heavy .zshrc loading for non-interactive
    **kwargs: Additional subprocess.Popen arguments

Returns:
    Popen process object

```python
popen_shell_command(cmd, shell, optimize_startup)
```

---

## reset_shell_cache

Reset shell cache (useful for testing or config changes).

---

## run_shell_command

Run shell command using fastest available shell.

Args:
    cmd: Command string or list to execute
    shell: Shell executable path (defaults to fastest available)
    optimize_startup: Skip heavy .zshrc loading for non-interactive
    capture_output: Capture stdout/stderr (default: True)
    **kwargs: Additional subprocess.run arguments

Returns:
    CompletedProcess result

```python
run_shell_command(cmd, shell, optimize_startup, capture_output)
```

---

