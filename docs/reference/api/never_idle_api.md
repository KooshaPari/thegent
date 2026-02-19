# never_idle API Reference

> **Source**: `src/thegent/sitback/never_idle.py`

Never-idle loop engine for Sitback Agent.

Provides continuous resident loop with:
- Non-blocking background task completion detection
- Rotating gardening checks
- Wake-on-completion callbacks

---

## NeverIdleLoop

Resident never-idle loop for Sitback Agent.

Runs continuously with configurable sleep interval between iterations.
Checks for background task completions (non-blocking) and runs gardening steps.

### Methods

#### NeverIdleLoop.__init__

Initialize the never-idle loop.

Args:
    session_dir: Path to session directory. Defaults to ~/.thegent/sessions/
    sleep_interval: Seconds to sleep between iterations. Default 45.
    project_root: Root directory for gardening. Defaults to cwd.

```python
__init__(self, session_dir, sleep_interval, project_root)
```

#### NeverIdleLoop.current_step

Return the current gardening step name.

```python
current_step(self)
```

#### NeverIdleLoop.get_findings

Return gardening findings that need attention.

```python
get_findings(self)
```

#### NeverIdleLoop.get_last_completion

Return last background task completion info.

```python
get_last_completion(self)
```

#### NeverIdleLoop.get_status

Get current status of the never-idle loop.

```python
get_status(self)
```

#### NeverIdleLoop.is_running

Return whether the loop is currently running.

```python
is_running(self)
```

#### NeverIdleLoop.register_wake_callback

Register a callback to be called when background task completes.

Args:
    callback: Function(list of (session_id, exit_code)) to call.

```python
register_wake_callback(self, callback)
```

#### NeverIdleLoop.start

Start the never-idle loop in a background thread.

```python
start(self)
```

#### NeverIdleLoop.stop

Stop the never-idle loop.

```python
stop(self)
```

---

## current_step

Return the current gardening step name.

```python
current_step(self)
```

---

## get_findings

Return gardening findings that need attention.

```python
get_findings(self)
```

---

## get_last_completion

Return last background task completion info.

```python
get_last_completion(self)
```

---

## get_never_idle

Get the global never-idle loop instance.

---

## get_never_idle_status

Get status of the global never-idle loop.

---

## get_status

Get current status of the never-idle loop.

```python
get_status(self)
```

---

## is_running

Return whether the loop is currently running.

```python
is_running(self)
```

---

## register_wake_callback

Register a callback to be called when background task completes.

Args:
    callback: Function(list of (session_id, exit_code)) to call.

```python
register_wake_callback(self, callback)
```

---

## start

Start the never-idle loop in a background thread.

```python
start(self)
```

---

## start_never_idle

Start the global never-idle loop.

Args:
    sleep_interval: Seconds between iterations.
    session_dir: Path to session directory.
    project_root: Root directory for gardening.

Returns:
    The started NeverIdleLoop instance.

```python
start_never_idle(sleep_interval, session_dir, project_root)
```

---

## stop

Stop the never-idle loop.

```python
stop(self)
```

---

## stop_never_idle

Stop the global never-idle loop.

---

