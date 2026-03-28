# cleanup API Reference

> **Source**: `src/thegent/process/cleanup.py`

Process Cleanup

Tracks and cleans up child processes on interrupt.

---

## ProcessCleanup

Tracks and cleans up child processes.

### Methods

#### ProcessCleanup.cleanup_all

```python
cleanup_all(self: Any)
```

Kill all registered processes.

---

#### ProcessCleanup.cleanup_on_signal

```python
cleanup_on_signal(self: Any, signum: int, frame: Any)
```

Signal handler for cleanup.

---

#### ProcessCleanup.register

```python
register(self: Any, pid: int)
```

Register a process for cleanup.

---

#### ProcessCleanup.unregister

```python
unregister(self: Any, pid: int)
```

Unregister a process.

---

---

## cleanup_all

```python
cleanup_all(self: Any)
```

Kill all registered processes.

---

## cleanup_on_signal

```python
cleanup_on_signal(self: Any, signum: int, frame: Any)
```

Signal handler for cleanup.

---

## register

```python
register(self: Any, pid: int)
```

Register a process for cleanup.

---

## register_cleanup

```python
register_cleanup(pid: int)
```

Register a process for cleanup on exit/interrupt.

---

## unregister

```python
unregister(self: Any, pid: int)
```

Unregister a process.

---

