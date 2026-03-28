# multi_runtime_diagnostics API Reference

> **Source**: `src/thegent/infra/multi_runtime_diagnostics.py`

Multi-runtime diagnostics for PyPy, CPython, Rust, Go, and Mojo.

This module provides comprehensive health checks for all runtimes in the
polyglot architecture.

---

## RuntimeStatus

Status of a runtime.

### Methods

---

## check_all_runtimes

```python
check_all_runtimes(mesh_root: Any)
```

Check all runtimes and hardware context.

---

## check_cpython_313

Check CPython 3.13 runtime availability and health.

---

## check_cpython_314

Check CPython 3.14 runtime availability and health.

---

## check_go

Check Go runtime availability and health.

---

## check_hardware

Check hardware-specific performance features.

---

## check_ipc_mesh

```python
check_ipc_mesh(mesh_root: Path)
```

Verify IPC mesh connectivity and performance.

---

## check_mojo

Check Mojo runtime availability and health.

---

## check_network_latency

```python
check_network_latency(target_host: str)
```

Check network latency to a target host.

---

## check_pypy

Check PyPy runtime availability and health.

---

## check_rust

Check Rust runtime availability and health.

---

## check_zig

Check Zig runtime availability and health.

---

## display_runtime_status

```python
display_runtime_status(data: dict[(str, Any)])
```

Display runtime status and hardware context in a formatted table.

---

