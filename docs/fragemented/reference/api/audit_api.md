# audit API Reference

> **Source**: `src/thegent/governance/audit.py`

Immutable audit trail and query interface (WP-3004, FR-012).

---

## query_events

```python
query_events(session_dir: Path, run_id: Any, event_type: Any, limit: int)
```

Query audit events from the registry.

---

## verify_chain

```python
verify_chain(session_dir: Path)
```

Verify hash chain integrity of the run registry.

---
