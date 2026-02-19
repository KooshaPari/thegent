# watchdog API Reference

> **Source**: `src/thegent/sitback/watchdog.py`

Background task watcher for non-blocking completion detection.

Provides polling-based detection of background task completion without blocking.
Used by the never-idle loop to wake on task completion.

---

## BackgroundTaskWatcher

Non-blocking watcher for background task completion.

Polls run_registry.jsonl for 'finish' events and checks session RC files.
Supports callback registration for completion notifications.

### Methods

#### BackgroundTaskWatcher.__init__

Initialize the watcher.

Args:
    session_dir: Path to session directory. Defaults to ~/.thegent/sessions/
    poll_interval: Polling interval in seconds. Default 2.0

```python
__init__(self, session_dir, poll_interval)
```

#### BackgroundTaskWatcher.check_completions

Check for newly completed tasks.

Polls run_registry.jsonl for 'finish' events and checks session RC files.

Returns:
    List of (session_id, exit_code) tuples for newly completed tasks.

```python
check_completions(self)
```

#### BackgroundTaskWatcher.get_known_sessions

Return set of known session IDs.

```python
get_known_sessions(self)
```

#### BackgroundTaskWatcher.register_callback

Register a callback to be called on task completion.

Args:
    callback: Function(session_id, exit_code) to call when task completes.

```python
register_callback(self, callback)
```

#### BackgroundTaskWatcher.reset

Reset state (for testing).

```python
reset(self)
```

#### BackgroundTaskWatcher.run_once

Run one check cycle, trigger callbacks, return completions.

Returns:
    List of (session_id, exit_code) tuples for completed tasks.

```python
run_once(self)
```

#### BackgroundTaskWatcher.wait_for_completion

Wait for any task to complete.

This is a blocking wait with timeout. For non-blocking use run_once().

Args:
    timeout: Maximum seconds to wait. None = wait forever.

Returns:
    List of (session_id, exit_code) tuples for completed tasks.

```python
wait_for_completion(self, timeout)
```

---

## check_completions

Check for newly completed tasks.

Polls run_registry.jsonl for 'finish' events and checks session RC files.

Returns:
    List of (session_id, exit_code) tuples for newly completed tasks.

```python
check_completions(self)
```

---

## get_known_sessions

Return set of known session IDs.

```python
get_known_sessions(self)
```

---

## register_callback

Register a callback to be called on task completion.

Args:
    callback: Function(session_id, exit_code) to call when task completes.

```python
register_callback(self, callback)
```

---

## reset

Reset state (for testing).

```python
reset(self)
```

---

## run_once

Run one check cycle, trigger callbacks, return completions.

Returns:
    List of (session_id, exit_code) tuples for completed tasks.

```python
run_once(self)
```

---

## wait_for_completion

Wait for any task to complete.

This is a blocking wait with timeout. For non-blocking use run_once().

Args:
    timeout: Maximum seconds to wait. None = wait forever.

Returns:
    List of (session_id, exit_code) tuples for completed tasks.

```python
wait_for_completion(self, timeout)
```

---

