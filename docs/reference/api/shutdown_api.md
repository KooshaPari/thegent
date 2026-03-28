# shutdown API Reference

> **Source**: `src/thegent/production/shutdown.py`

Graceful Shutdown

Handles graceful shutdown with cleanup.

---

## GracefulShutdown

Manages graceful shutdown.

### Methods

#### GracefulShutdown.__init__

```python
__init__(self: Any, timeout: float)
```

---

#### GracefulShutdown.install

```python
install(self: Any)
```

Install signal handlers.

---

#### GracefulShutdown.is_shutting_down

```python
is_shutting_down(self: Any)
```

Check if shutting down.

---

#### GracefulShutdown.register

```python
register(self: Any, handler: Callable)
```

Register a shutdown handler.

---

#### GracefulShutdown.shutdown

```python
shutdown(self: Any)
```

Trigger shutdown programmatically.

---

#### GracefulShutdown.uninstall

```python
uninstall(self: Any)
```

Restore original signal handlers.

---

---

## ShutdownContext

Context manager for shutdown-aware operations.

### Methods

#### ShutdownContext.__init__

```python
__init__(self: Any, shutdown: GracefulShutdown)
```

---

#### ShutdownContext.check

```python
check(self: Any)
```

Check if should continue.

---

---

## check

```python
check(self: Any)
```

Check if should continue.

---

## install

```python
install(self: Any)
```

Install signal handlers.

---

## is_shutting_down

```python
is_shutting_down(self: Any)
```

Check if shutting down.

---

## register

```python
register(self: Any, handler: Callable)
```

Register a shutdown handler.

---

## shutdown

```python
shutdown(self: Any)
```

Trigger shutdown programmatically.

---

## uninstall

```python
uninstall(self: Any)
```

Restore original signal handlers.

---

