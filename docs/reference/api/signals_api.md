# signals API Reference

> **Source**: `src/thegent/process/signals.py`

Signal Handler

Registers handlers for graceful shutdown.

---

## SignalHandler

Handles system signals for graceful shutdown.

### Methods

#### SignalHandler.__init__

```python
__init__(self: Any)
```

---

#### SignalHandler.install

```python
install(self: Any)
```

Install signal handlers.

---

#### SignalHandler.on_shutdown

```python
on_shutdown(self: Any, callback: Callable[(Any, object)])
```

Register callback for shutdown.

---

#### SignalHandler.restore

```python
restore(self: Any)
```

Restore original signal handlers.

---

---

## install

```python
install(self: Any)
```

Install signal handlers.

---

## install_signal_handlers

Install global signal handlers.

---

## on_shutdown

```python
on_shutdown(self: Any, callback: Callable[(Any, object)])
```

Register callback for shutdown.

---

## restore

```python
restore(self: Any)
```

Restore original signal handlers.

---

