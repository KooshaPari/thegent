# process_registry API Reference

> **Source**: `src/thegent/infra/process_registry.py`

Process registry for tracking and cleaning up subprocesses.

---

## ProcessHandle

Handle for a tracked subprocess.

### Methods

#### ProcessHandle.get_psutil_process

Get psutil Process object for introspection.

Returns:
    psutil.Process object, or None if process not found.

```python
get_psutil_process(self)
```

#### ProcessHandle.get_resource_usage

Get resource usage using psutil.

Returns:
    Dictionary with resource usage information, or None if unavailable.

```python
get_resource_usage(self)
```

#### ProcessHandle.is_alive

Check if process is still running.

```python
is_alive(self)
```

#### ProcessHandle.terminate

Terminate process gracefully.

```python
terminate(self, timeout)
```

---

## ProcessRegistry

Registry for tracking subprocesses with automatic cleanup.

### Methods

#### ProcessRegistry.__init__

```python
__init__(self)
```

#### ProcessRegistry.cleanup_all

Clean up all registered processes.

```python
cleanup_all(self, timeout)
```

#### ProcessRegistry.cleanup_orphaned

Clean up processes that have died but weren't unregistered.

```python
cleanup_orphaned(self)
```

#### ProcessRegistry.cleanup_process_tree

Clean up process and all children using psutil.

Args:
    pid: Process ID to clean up.
    timeout: Timeout in seconds for process termination.

Returns:
    Number of processes cleaned up.

```python
cleanup_process_tree(self, pid, timeout)
```

#### ProcessRegistry.get

Get process handle by PID.

```python
get(self, pid)
```

#### ProcessRegistry.get_stats

Get registry statistics.

```python
get_stats(self)
```

#### ProcessRegistry.list_alive

List all alive processes.

```python
list_alive(self)
```

#### ProcessRegistry.register

Register a process for tracking.

```python
register(self, proc, name, cleanup_on_exit, timeout)
```

#### ProcessRegistry.unregister

Unregister a process.

```python
unregister(self, pid)
```

---

## cleanup_all

Clean up all registered processes.

```python
cleanup_all(self, timeout)
```

---

## cleanup_orphaned

Clean up processes that have died but weren't unregistered.

```python
cleanup_orphaned(self)
```

---

## cleanup_process_tree

Clean up process and all children using psutil.

Args:
    pid: Process ID to clean up.
    timeout: Timeout in seconds for process termination.

Returns:
    Number of processes cleaned up.

```python
cleanup_process_tree(self, pid, timeout)
```

---

## get

Get process handle by PID.

```python
get(self, pid)
```

---

## get_psutil_process

Get psutil Process object for introspection.

Returns:
    psutil.Process object, or None if process not found.

```python
get_psutil_process(self)
```

---

## get_registry

Get global process registry.

---

## get_resource_usage

Get resource usage using psutil.

Returns:
    Dictionary with resource usage information, or None if unavailable.

```python
get_resource_usage(self)
```

---

## get_stats

Get registry statistics.

```python
get_stats(self)
```

---

## is_alive

Check if process is still running.

```python
is_alive(self)
```

---

## list_alive

List all alive processes.

```python
list_alive(self)
```

---

## register

Register a process for tracking.

```python
register(self, proc, name, cleanup_on_exit, timeout)
```

---

## terminate

Terminate process gracefully.

```python
terminate(self, timeout)
```

---

## unregister

Unregister a process.

```python
unregister(self, pid)
```

---

