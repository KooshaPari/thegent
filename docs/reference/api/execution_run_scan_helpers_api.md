# execution_run_scan_helpers API Reference

> **Source**: `src/thegent/execution_run_scan_helpers.py`

Helpers for scanning run registry JSONL lines.

---

## check_session_id

```python
check_session_id(line: str, session_id: str)
```

Check if a line matches the session ID.

---

## extract_domain_tag

```python
extract_domain_tag(line: str)
```

Extract run_id and domain_tag.

---

## extract_run_id

```python
extract_run_id(line: str)
```

Extract run ID from a registry line.

---

## extract_session_id

```python
extract_session_id(line: str)
```

Extract session ID from a registry line.

---

## filter_expired_record

```python
filter_expired_record(line: str, now: datetime, run_domains: dict[(str, str)], default_days: int, by_domain: dict[(str, int)])
```

Check if a record is expired. Returns (is_expired, line).

---

## process_calibration_entry

```python
process_calibration_entry(line: str, agent: str, runs: dict[(str, dict[(str, Any)])])
```

Process an entry for calibration calculation.

---

## process_run_entry

```python
process_run_entry(line: str, runs: dict[(str, dict[(str, Any)])])
```

Process a run entry and update the in-memory run map.

---

## process_token_match

```python
process_token_match(line: str, token: str, best: Any)
```

Process a line for idempotency token matching.

---

## update_run_state

```python
update_run_state(line: str, run_id: str, current_state: Any, run_state_cls: Any)
```

Update run state from a registry line.

---

