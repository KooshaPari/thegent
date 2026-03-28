# session_snapshot_cli_helpers API Reference

> **Source**: `src/thegent/orchestration/state/session_snapshot_cli_helpers.py`

Payload helpers for snapshot CLI commands.

---

## _PruneSnapshotsCallable

**Inherits from**: `Protocol`

### Methods

---

## snapshot_daily_export_payload

```python
snapshot_daily_export_payload(scraper: Any, out_path: Any, limit: int, trigger: Any, tag: Any, since: Any) -> dict[(str, Any)]
```

---

## snapshot_daily_index_payload

```python
snapshot_daily_index_payload(scraper: Any, limit: int, trigger: Any, tag: Any, since: Any) -> dict[(str, Any)]
```

---

## snapshot_daily_totals_payload

```python
snapshot_daily_totals_payload(scraper: Any, limit: int, trigger: Any, tag: Any, since: Any)
```

Return only daily aggregate totals for lightweight CLI/report views.

---

## snapshot_export_payload

```python
snapshot_export_payload(scraper: Any, snapshot_path: str, out_path: Any) -> dict[(str, Any)]
```

---

## snapshot_index_payload

```python
snapshot_index_payload(scraper: Any, limit: int) -> dict[(str, Any)]
```

---

## snapshot_list_payload

```python
snapshot_list_payload(scraper: Any, limit: int, trigger: Any, tag: Any, since: Any) -> dict[(str, Any)]
```

---

## snapshot_prune_payload

```python
snapshot_prune_payload(scraper: Any, max_keep: int) -> dict[(str, int)]
```

---

## snapshot_triggers_tags_payload

```python
snapshot_triggers_tags_payload(scraper: Any, limit: int) -> dict[(str, list[str])]
```

---

