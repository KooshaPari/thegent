# isolation API Reference

> **Source**: `src/thegent/cli/apps/isolation.py`

Thegent Isolation: Multi-tenancy and Sandboxing Control.

---

## isolation_check

```python
isolation_check(mode: str)
```

Check the status of the isolation system.

---

## isolation_share_run

```python
isolation_share_run(command: list[str], tenant_id: str, role: Any)
```

Run a command shared across tenants using CLI-Share debouncing.

---

