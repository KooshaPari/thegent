# audit API Reference

> **Source**: `src/thegent/governance/audit.py`

Immutable audit trail and query interface (WP-3004, FR-012).

---

## query_events

Query audit events from the registry.

```python
query_events(session_dir, run_id, event_type, limit)
```

---

## verify_chain

Verify hash chain integrity of the run registry.

```python
verify_chain(session_dir)
```

---

