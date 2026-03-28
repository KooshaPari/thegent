# oversight API Reference

> **Source**: `src/thegent/orchestration/resilience/oversight.py`

Controlled oversight for repeated failures (WP-2008, FR-009).

---

## get_oversight_action

```python
get_oversight_action(failure_count: int)
```

Return recommended oversight action: Union[pause, escalate] | continue.

---

## should_trigger_oversight

```python
should_trigger_oversight(session_dir: Path, target: str, failure_count: int, threshold: int)
```

True if repeated failures exceed threshold and oversight should trigger.

---

