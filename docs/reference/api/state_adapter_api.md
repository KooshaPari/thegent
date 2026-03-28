# state_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/state_adapter.py`

State management adapter for workstream autosync.

Handles local state persistence, checkpoints, and trends.

---

## StateAdapter

Adapter for state management operations.

### Methods

#### StateAdapter.__init__

```python
__init__(self: Any, config: Any)
```

---

#### StateAdapter.append_trend_sample

```python
append_trend_sample(self: Any, sample: dict[(str, Any)])
```

Append trend sample to file.

---

#### StateAdapter.compact_snapshots

```python
compact_snapshots(self: Any, keep_count: int)
```

Compact old snapshots, keeping only the most recent.

---

#### StateAdapter.get_autosync_metrics_path

```python
get_autosync_metrics_path(self: Any)
```

---

#### StateAdapter.get_change_digest_path

```python
get_change_digest_path(self: Any)
```

---

#### StateAdapter.get_checkpoint_path

```python
get_checkpoint_path(self: Any, checkpoint_id: str)
```

Get path for checkpoint file.

---

#### StateAdapter.get_cycle_manifest_path

```python
get_cycle_manifest_path(self: Any)
```

---

#### StateAdapter.get_cycle_metrics_path

```python
get_cycle_metrics_path(self: Any)
```

---

#### StateAdapter.get_failure_queue_path

```python
get_failure_queue_path(self: Any)
```

---

#### StateAdapter.get_latest_snapshot_age_seconds

```python
get_latest_snapshot_age_seconds(self: Any)
```

Get age of latest snapshot in seconds.

---

#### StateAdapter.get_snapshot_path

```python
get_snapshot_path(self: Any)
```

Get path for snapshot file.

---

#### StateAdapter.get_status_path

```python
get_status_path(self: Any)
```

---

#### StateAdapter.get_trend_path

```python
get_trend_path(self: Any)
```

---

#### StateAdapter.read_last_manifest_hash

```python
read_last_manifest_hash(self: Any)
```

Read last manifest hash from status.

---

#### StateAdapter.write_status

```python
write_status(self: Any, status: dict[(str, Any)])
```

Write status to file.

---

---

## StateAdapterWrapper

State adapter wrapper for registry.

### Methods

#### StateAdapterWrapper.__init__

```python
__init__(self: Any, config: Any)
```

---

#### StateAdapterWrapper.call

```python
call(self: Any)
```

---

---

## append_trend_sample

```python
append_trend_sample(self: Any, sample: dict[(str, Any)])
```

Append trend sample to file.

---

## call

```python
call(self: Any) -> dict[(str, str)]
```

---

## compact_snapshots

```python
compact_snapshots(self: Any, keep_count: int)
```

Compact old snapshots, keeping only the most recent.

---

## get_autosync_metrics_path

```python
get_autosync_metrics_path(self: Any) -> Path
```

---

## get_change_digest_path

```python
get_change_digest_path(self: Any) -> Path
```

---

## get_checkpoint_path

```python
get_checkpoint_path(self: Any, checkpoint_id: str)
```

Get path for checkpoint file.

---

## get_cycle_manifest_path

```python
get_cycle_manifest_path(self: Any) -> Path
```

---

## get_cycle_metrics_path

```python
get_cycle_metrics_path(self: Any) -> Path
```

---

## get_failure_queue_path

```python
get_failure_queue_path(self: Any) -> Path
```

---

## get_latest_snapshot_age_seconds

```python
get_latest_snapshot_age_seconds(self: Any)
```

Get age of latest snapshot in seconds.

---

## get_snapshot_path

```python
get_snapshot_path(self: Any)
```

Get path for snapshot file.

---

## get_status_path

```python
get_status_path(self: Any) -> Path
```

---

## get_trend_path

```python
get_trend_path(self: Any) -> Path
```

---

## read_last_manifest_hash

```python
read_last_manifest_hash(self: Any)
```

Read last manifest hash from status.

---

## write_status

```python
write_status(self: Any, status: dict[(str, Any)])
```

Write status to file.

---

