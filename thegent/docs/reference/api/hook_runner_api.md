# hook_runner API Reference

> **Source**: `src/thegent/infra/hook_runner.py`

Hook runner with shell detection and cross-platform support.

---

## main

CLI entry point for running a hook.

---

## run_hook

```python
run_hook(hook_path: Path, input_data: Any, timeout: int)
```

Run a hook script using the preferred shell.

---
