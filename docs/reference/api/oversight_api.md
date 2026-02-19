# oversight API Reference

> **Source**: `src/thegent/orchestration/oversight.py`

Controlled oversight for repeated failures (WP-2008, FR-009).

---

## get_oversight_action

Return recommended oversight action: Union[pause, escalate] | continue.

```python
get_oversight_action(failure_count)
```

---

## should_trigger_oversight

True if repeated failures exceed threshold and oversight should trigger.

```python
should_trigger_oversight(session_dir, target, failure_count, threshold)
```

---

