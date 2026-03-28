# install_powershell API Reference

> **Source**: `src/thegent/install_powershell.py`

PowerShell-specific install helpers for mise shell activation.

---

## detect_powershell_profile

Return the PowerShell profile path for the current user.

---

## is_powershell_environment

Return True when the active shell is PowerShell or the platform is Windows.

---

## write_powershell_mise_hook

```python
write_powershell_mise_hook(profile_path: Path, console: Any, dry_run: bool)
```

Append the mise activation hook to a PowerShell profile file (idempotent).

---

