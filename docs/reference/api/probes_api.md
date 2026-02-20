# probes API Reference

> **Source**: `src/thegent/orchestration/probes.py`

Regression prevention probes (WP-2006, FR-005).

---

## run_post_rollback_probes

```python
run_post_rollback_probes(session_dir: Path)
```

Run probes after rollback to verify state.

---

## run_pre_promote_probes

```python
run_pre_promote_probes(session_dir: Path)
```

Run probes before promotion gate. Returns pass/fail and findings.

---

