# execution_io API Reference

> **Source**: `src/thegent/adapters/execution_io.py`

I/O and subprocess management for task execution.

Handles:
- Shadow workspace creation/cleanup
- Resource locking
- Subprocess spawning with keepalive
- File I/O for session artifacts
- Process environment setup

---

## ProcessEnvironmentBuilder

Builds environment for subprocess execution.

### Methods

#### ProcessEnvironmentBuilder.apply_sandbox_wrapper

```python
apply_sandbox_wrapper(cmd: list[str], settings: Any, project_root: Path)
```

Apply macOS sandbox wrapping if configured.

---

#### ProcessEnvironmentBuilder.build_env

```python
build_env(session_id: str, session_paths: dict[(str, Path)], owner_tag: str, shadow_env: Any, filter_env: bool, allowlist: Any)
```

Build subprocess environment dict.

---

---

## ProcessSpawner

Spawns and monitors subprocess execution.

### Methods

#### ProcessSpawner.cleanup_stdin

```python
cleanup_stdin(stdin_handle: Any)
```

Clean up stdin file descriptor if it's an FD.

---

#### ProcessSpawner.setup_fifo_stdin

```python
setup_fifo_stdin(fifo_path: Path)
```

Set up FIFO for stdin on Unix systems.

Returns file descriptor or None if not supported.

---

#### ProcessSpawner.spawn_process

```python
spawn_process(cmd: list[str], cwd: str, env: dict[(str, str)], stdin_handle: Any, stdout_handle: Any, stderr_handle: Any, spawn_fn: Any)
```

Spawn subprocess with given configuration.

spawn_fn: Optional custom spawner (defaults to subprocess.Popen).

---

---

## ResourceLockManager

Manages resource file leases for concurrency control.

### Methods

#### ResourceLockManager.acquire_locks

```python
acquire_locks(lock_paths: list[str], run_id: str, timeout: int, session_dir: Path, base_cwd: Path)
```

Acquire leases for locked resources.

Returns list of (path, token) tuples for locked resources.
Raises RuntimeError if any lock fails.

---

#### ResourceLockManager.release_locks

```python
release_locks(locked_tokens: list[tuple[(Path, str)]], run_id: str, session_dir: Path)
```

Release all acquired resource leases.

---

---

## ShadowWorkspaceManager

Manages shadow workspace lifecycle.

### Methods

#### ShadowWorkspaceManager.cleanup

```python
cleanup(shadow_ws: Any)
```

Clean up shadow workspace if it was created.

---

#### ShadowWorkspaceManager.create_if_enabled

```python
create_if_enabled(original_cwd: Path, run_id: str, enabled: bool)
```

Create shadow workspace if enabled.

Returns (shadow_ws, agent_cwd, shadow_env).
- If not enabled or creation fails: (None, original_cwd, None)

---

#### ShadowWorkspaceManager.merge_back

```python
merge_back(shadow_ws: Any, auto_merge: bool)
```

Merge shadow workspace changes back to main project.

---

---

## acquire_locks

```python
acquire_locks(lock_paths: list[str], run_id: str, timeout: int, session_dir: Path, base_cwd: Path)
```

Acquire leases for locked resources.

Returns list of (path, token) tuples for locked resources.
Raises RuntimeError if any lock fails.

---

## apply_sandbox_wrapper

```python
apply_sandbox_wrapper(cmd: list[str], settings: Any, project_root: Path)
```

Apply macOS sandbox wrapping if configured.

---

## build_env

```python
build_env(session_id: str, session_paths: dict[(str, Path)], owner_tag: str, shadow_env: Any, filter_env: bool, allowlist: Any)
```

Build subprocess environment dict.

---

## cleanup

```python
cleanup(shadow_ws: Any)
```

Clean up shadow workspace if it was created.

---

## cleanup_stdin

```python
cleanup_stdin(stdin_handle: Any)
```

Clean up stdin file descriptor if it's an FD.

---

## create_if_enabled

```python
create_if_enabled(original_cwd: Path, run_id: str, enabled: bool)
```

Create shadow workspace if enabled.

Returns (shadow_ws, agent_cwd, shadow_env).
- If not enabled or creation fails: (None, original_cwd, None)

---

## merge_back

```python
merge_back(shadow_ws: Any, auto_merge: bool)
```

Merge shadow workspace changes back to main project.

---

## release_locks

```python
release_locks(locked_tokens: list[tuple[(Path, str)]], run_id: str, session_dir: Path)
```

Release all acquired resource leases.

---

## setup_fifo_stdin

```python
setup_fifo_stdin(fifo_path: Path)
```

Set up FIFO for stdin on Unix systems.

Returns file descriptor or None if not supported.

---

## spawn_process

```python
spawn_process(cmd: list[str], cwd: str, env: dict[(str, str)], stdin_handle: Any, stdout_handle: Any, stderr_handle: Any, spawn_fn: Any)
```

Spawn subprocess with given configuration.

spawn_fn: Optional custom spawner (defaults to subprocess.Popen).

---

