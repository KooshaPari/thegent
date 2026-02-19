# fast_subprocess API Reference

> **Source**: `src/thegent/infra/fast_subprocess.py`

Fast subprocess execution with async support and optimizations.

This module provides optimized subprocess execution with:
- Async subprocess support for concurrent execution
- Optimized process creation and management
- Better resource usage for concurrent operations
- Platform-specific optimizations

Performance improvements:
- Async execution for concurrent subprocesses (non-blocking)
- Optimized process creation flags
- Better resource management

---

## FastSubprocess

High-performance subprocess execution with async support.

### Methods

#### FastSubprocess.run_optimized

Run subprocess with optimizations (synchronous).

Args:
    cmd: Command and arguments
    cwd: Working directory
    env: Environment variables
    timeout: Timeout in seconds
    check: Raise exception on non-zero exit
    capture_output: Capture stdout/stderr
    start_new_session: Start new session (Unix)
    close_fds: Close file descriptors (Unix)
    **kwargs: Additional subprocess options

Returns:
    CompletedProcess with stdout, stderr, returncode

Optimizations:
    - start_new_session for daemon processes
    - close_fds to prevent FD leaks
    - Optimized process creation flags

```python
run_optimized(cmd)
```

---

## run_optimized

Run subprocess with optimizations (synchronous).

Args:
    cmd: Command and arguments
    cwd: Working directory
    env: Environment variables
    timeout: Timeout in seconds
    check: Raise exception on non-zero exit
    capture_output: Capture stdout/stderr
    start_new_session: Start new session (Unix)
    close_fds: Close file descriptors (Unix)
    **kwargs: Additional subprocess options

Returns:
    CompletedProcess with stdout, stderr, returncode

Optimizations:
    - start_new_session for daemon processes
    - close_fds to prevent FD leaks
    - Optimized process creation flags

```python
run_optimized(cmd)
```

---

## run_subprocess_optimized

Run subprocess with optimizations.

```python
run_subprocess_optimized(cmd)
```

---

