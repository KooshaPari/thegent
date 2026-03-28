# run_observe_helpers API Reference

> **Source**: `src/thegent/cli/services/run_observe_helpers.py`

Observe-summary trend/snapshot helper services extracted from CLI impl surface.

---

## append_health_snapshot

```python
append_health_snapshot(payload: dict[(str, Any)], scope_key: dict[(str, Any)]) -> None
```

---

## append_observe_summary_snapshot

```python
append_observe_summary_snapshot(payload: dict[(str, Any)], trend_scope_key: dict[(str, Any)], trend_scope_signature: str, scope_key_json: str, trend_snapshot_ids: list[str], trend_summary: dict[(str, Any)]) -> None
```

---

## build_observe_summary_trend_scope

---

## classify_observe_summary_trend_health

---

## compact_health_snapshot_log

---

## hash_health_payload

```python
hash_health_payload(payload: dict[(str, Any)])
```

Return a stable hash for a health payload while ignoring timestamp/signature fields.

---

## hash_observe_summary_payload

```python
hash_observe_summary_payload(payload: dict[(str, Any)])
```

Return a stable hash for an observe-summary payload.

---

## hash_observe_summary_trend_scope

```python
hash_observe_summary_trend_scope(scope_key: dict[(str, Any)]) -> str
```

---

## health_snapshot_log_path

---

## health_snapshot_max_lines

---

## load_observe_summary_snapshots

```python
load_observe_summary_snapshots(scope_signature: str, scope_key_json: str, limit: int) -> list[dict[(str, Any)]]
```

---

## load_previous_health_snapshot

```python
load_previous_health_snapshot(scope_key: dict[(str, Any)]) -> Any
```

---

## observe_summary_freshness_bucket

```python
observe_summary_freshness_bucket(freshness_seconds: Any) -> str
```

---

## parse_observe_summary_env_float

```python
parse_observe_summary_env_float(name: str, default: float) -> float
```

---

## parse_observe_summary_env_int

```python
parse_observe_summary_env_int(name: str, default: int) -> int
```

---

## parse_observe_summary_timestamp

```python
parse_observe_summary_timestamp(value: Any) -> Any
```

---

