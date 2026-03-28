# clode_config_isolation API Reference

> **Source**: `src/thegent/clode_config_isolation.py`

Claude config isolation helpers for clode.

---

## CleanupDiagnostics

**Inherits from**: `TypedDict`

---

## CleanupFailure

**Inherits from**: `TypedDict`

---

## IsolationDiagnostics

**Inherits from**: `TypedDict`

---

## SettingsCopyDiagnostics

**Inherits from**: `TypedDict`

---

## ensure_claude_config_isolation

```python
ensure_claude_config_isolation(config_dir: Path)
```

Ensure isolated config dir links to global state and onboarding/session data.

---

## get_isolation_diagnostics

Return diagnostics for config isolation setup.

---

## reset_isolation_diagnostics

Reset diagnostics (test helper).

---

