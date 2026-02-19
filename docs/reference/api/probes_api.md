# probes API Reference

> **Source**: `src/thegent/orchestration/probes.py`

Regression prevention probes (WP-2006, FR-005).

---

## run_post_rollback_probes

Run probes after rollback to verify state.

```python
run_post_rollback_probes(session_dir)
```

---

## run_pre_promote_probes

Run probes before promotion gate. Returns pass/fail and findings.

```python
run_pre_promote_probes(session_dir)
```

---

