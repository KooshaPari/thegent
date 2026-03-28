# execution_event_builders API Reference

> **Source**: `src/thegent/execution_event_builders.py`

Factory helpers for execution registry event payloads.

---

## build_feedback_event

```python
build_feedback_event(run_id: str, score: float, note: Any, prev_hash: Any)
```

Create a run-feedback event payload.

---

## build_finish_event

```python
build_finish_event(run_id: str, exit_code: int, status: str, ended_at_utc: str, duration_s: float, error_class: Any, prev_hash: Any, cost_usd: Any, event_details: Any)
```

Create a run-finish event payload.

---

## build_pause_event

```python
build_pause_event(run_id: str, reason: str, continuity_snapshot: Any, prev_hash: Any)
```

Create a run-pause event payload.

---

## build_resume_event

```python
build_resume_event(run_id: str, prev_hash: Any)
```

Create a run-resume event payload.

---

## build_schema_marker_event

```python
build_schema_marker_event(schema_version: int)
```

Create the schema marker event payload.

---

