# executor API Reference

> **Source**: `src/thegent/shell/executor.py`

Shell Executor

Executes shell commands with timeout, retry, and error handling.

---

## ShellExecutor

Shell command executor with retry and timeout.

### Methods

#### ShellExecutor.__init__

```python
__init__(self: Any, config: Optional[ShellConfig])
```

---

#### ShellExecutor.cancel

```python
cancel(self: Any)
```

Cancel running command.

---

#### ShellExecutor.run

```python
run(self: Any, command: str, timeout: Optional[float], cwd: Optional[str], env: Optional[dict])
```

Execute command with retry logic.

---

---

## ShellResult

Result of shell command execution.

### Methods

#### ShellResult.success

```python
success(self: Any)
```

---

---

## cancel

```python
cancel(self: Any)
```

Cancel running command.

---

## run

```python
run(self: Any, command: str, timeout: Optional[float], cwd: Optional[str], env: Optional[dict])
```

Execute command with retry logic.

---

## success

```python
success(self: Any) -> bool
```

---

