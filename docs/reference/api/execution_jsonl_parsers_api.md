# execution_jsonl_parsers API Reference

> **Source**: `src/thegent/execution_jsonl_parsers.py`

JSONL parsing helpers used by execution registries.

---

## get_native_parse_diagnostics

Return snapshot of native parse diagnostics counters.

---

## parse_checkpoint_by_id

```python
parse_checkpoint_by_id(line: str, checkpoint_id: str)
```

Parse a checkpoint line and check if ID matches.

---

## parse_checkpoint_line

```python
parse_checkpoint_line(line: str)
```

Parse a checkpoint registry line.

---

## parse_circuit_failure

```python
parse_circuit_failure(line: str, target: str, category: str, now: datetime, window_s: int)
```

Parse a circuit breaker failure line.

---

## parse_dlq_item

```python
parse_dlq_item(line: str, status: Any, run_id: Any)
```

Parse a single DLQ item with optional filtering.

---

## parse_fatigue_line

```python
parse_fatigue_line(line: str, now: datetime, window_s: int)
```

Parse a fatigue interruption line.

---

## parse_override_unexpired

```python
parse_override_unexpired(line: str, owner: str, now: datetime)
```

Parse an override line and check if it's unexpired.

---

## process_dlq_line

```python
process_dlq_line(line: str, run_id: str, resolution: str)
```

Update a DLQ line for resolution handling.

---

## reset_native_parse_diagnostics

Reset diagnostics counters (used by tests).

---

