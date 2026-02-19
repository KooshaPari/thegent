# utils API Reference

> **Source**: `src/thegent/utils/__init__.py`

Utility modules for thegent.

---

## get_resource_path

Get absolute path to a resource file.

In dev mode, looks in the project root.
When installed, uses importlib.resources.

```python
get_resource_path(relative_path)
```

---

## is_dev_mode

Check if thegent is running in development mode.

Dev mode is active if:
1. THGENT_DEV=1 is set in environment
2. We are running from a git repository and src/thegent exists

---

## strip_ansi

Remove ANSI escape sequences (colors, etc.) from text.
Uses rich.text.Text.from_ansi() which is the idiomatic way to strip ANSI in Rich.

```python
strip_ansi(text)
```

---

