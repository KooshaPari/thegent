# cli_concurrency API Reference

> **Source**: `src/thegent/cli_concurrency.py`

CLI commands for concurrency management.

---

## disable_load_based

```python
disable_load_based(session_dir: Any)
```

Disable load-based concurrency control.

---

## enable_load_based

```python
enable_load_based(session_dir: Any)
```

Enable load-based concurrency control.

---

## set_concurrency

```python
set_concurrency(max_concurrency: int, session_dir: Any)
```

Set concurrency limit (persistently in .env).

---

## show_concurrency

```python
show_concurrency(session_dir: Any)
```

Show current concurrency settings and status.

---

