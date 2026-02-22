# resources API Reference

> **Source**: `src/thegent/resources.py`

Resource access utilities for thegent.

---

## get_resource_path

```python
get_resource_path(relative_path: str)
```

Get absolute path to a resource file.

In dev mode (THGENT_DEV=1 or running from git), looks in the project root.
When installed, uses importlib.resources.

---
