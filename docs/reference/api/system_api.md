# system API Reference

> **Source**: `src/thegent/cli/apps/system.py`

System configuration management - Nix-like declarative system setup.

Usage:
    thegent system install --bundle dev
    thegent system install --target shells.zsh
    thegent system install --all
    thegent system verify
    thegent system status

---

## system_callback

```python
system_callback(ctx: typer.Context)
```

System configuration management.

---

## system_install

```python
system_install(target: str, bundle: str, dry_run: bool, verbose: bool)
```

Install system configurations.

---

## system_status

Show installation status.

---

## system_verify

```python
system_verify(target: str, verbose: bool)
```

Verify installed configurations.

---

