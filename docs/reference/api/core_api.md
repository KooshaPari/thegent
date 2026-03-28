# core API Reference

> **Source**: `src/thegent/doctor/core.py`

Doctor module for comprehensive health and preflight checks of thegent environment.

---

## ProcessInfo

Lightweight process information.

---

## run_doctor

```python
run_doctor(fix: bool, dry_run: bool, runtime: bool, network: bool, processes: bool, memory: bool, deps: bool)
```

Run all health checks and report results.

**Parameters**:

- `fix`: Attempt to fix detected issues
- `dry_run`: Show what fixes would be applied without making changes
- `runtime`: Show multi-runtime diagnostics
- `network`: Check network connectivity
- `processes`: Check process health
- `memory`: Check memory usage
- `deps`: Check dependencies

---

