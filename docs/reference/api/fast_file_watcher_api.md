# fast_file_watcher API Reference

> **Source**: `src/thegent/infra/fast_file_watcher.py`

Fast file watcher with optimized backends.

This module provides a high-performance abstraction layer for file watching
that automatically selects the fastest available backend:
- watchfiles (Rust-based): 5-10x faster than watchdog
- watchdog: Cross-platform fallback

Performance improvements:
- watchfiles uses Rust implementation (5-10x faster)
- Better performance for high-frequency file changes
- Automatic backend selection based on availability

---

## FastFileWatcher

High-performance file watcher with automatic backend selection.

Backend priority (fastest first):
1. watchfiles (if installed) - 5-10x faster, Rust-based
2. watchdog (cross-platform fallback) - baseline performance

### Methods

#### FastFileWatcher.__init__

Initialize file watcher.

Args:
    path: Directory or file to watch
    recursive: Whether to watch recursively

```python
__init__(self, path, recursive)
```

#### FastFileWatcher.backend

Get current backend name.

```python
backend(self)
```

#### FastFileWatcher.start

Start watching (watchdog backend).

Args:
    event_handler: Optional custom event handler

```python
start(self, event_handler)
```

#### FastFileWatcher.stop

Stop watching.

```python
stop(self)
```

#### FastFileWatcher.watch

Watch for file changes using watchfiles backend.

Args:
    callback: Function to call on changes
    **kwargs: Additional options for watchfiles

```python
watch(self, callback)
```

---

## SimpleHandler

**Inherits from**: `FileSystemEventHandler`

### Methods

#### SimpleHandler.on_any_event

```python
on_any_event(self, event)
```

---

## backend

Get current backend name.

```python
backend(self)
```

---

## on_any_event

```python
on_any_event(self, event)
```

---

## start

Start watching (watchdog backend).

Args:
    event_handler: Optional custom event handler

```python
start(self, event_handler)
```

---

## stop

Stop watching.

```python
stop(self)
```

---

## watch

Watch for file changes using watchfiles backend.

Args:
    callback: Function to call on changes
    **kwargs: Additional options for watchfiles

```python
watch(self, callback)
```

---

## watch_files

Watch files using fastest available backend (watchfiles preferred).

Args:
    path: Directory or file to watch
    callback: Function to call on changes
    recursive: Whether to watch recursively
    **kwargs: Additional options

```python
watch_files(path, callback, recursive)
```

---

