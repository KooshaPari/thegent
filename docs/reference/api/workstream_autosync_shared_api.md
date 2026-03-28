# workstream_autosync_shared API Reference

> **Source**: `src/thegent/integrations/workstream_autosync_shared.py`

Shared models, parser, and config loading for workstream autosync.

---

## ConnectorHealthProbeResult

Connector health probe state for a cycle.

### Methods

#### ConnectorHealthProbeResult.to_dict

```python
to_dict(self: Any)
```

---

---

## FailureRecord

Failure entry for queue pruning and retry heuristics.

### Methods

#### FailureRecord.to_dict

```python
to_dict(self: Any)
```

Serialize failure record.

---

---

## MaintenanceWindow

Parsed maintenance window configuration for a connector.

### Methods

#### MaintenanceWindow.is_active

```python
is_active(self: Any, now: datetime)
```

Return whether the window is active at the given timestamp.

---

---

## RemoteMissingItemPolicy

Policy for local WL items missing from remote connector snapshots.

**Inherits from**: `str, Enum`

---

## RetryClass

Error classes driving retry/backoff policy.

**Inherits from**: `str, Enum`

---

## SyncCheckpoint

Minimal checkpoint used for rolling resume.

**Inherits from**: `SerializableMixin`

### Methods

#### SyncCheckpoint.from_dict

```python
from_dict(cls: Any, payload: dict[(str, Any)])
```

Construct a checkpoint from serialized state.

---

---

## SyncCycleManifest

Append-only cycle manifest for reproducible autosync audit.

### Methods

#### SyncCycleManifest.to_dict

```python
to_dict(self: Any)
```

---

#### SyncCycleManifest.with_hash

```python
with_hash(self: Any)
```

Return a copy with deterministic manifest hash.

---

---

## SyncDirection

Sync direction (read-only, write-only, bidirectional).

**Inherits from**: `str, Enum`

---

## SyncFailureQueue

Store and prune recent sync failures.

### Methods

#### SyncFailureQueue.__init__

```python
__init__(self: Any, retention_seconds: int)
```

---

#### SyncFailureQueue.prune_expired

```python
prune_expired(self: Any, now: Any)
```

Drop failures older than retention window.

---

#### SyncFailureQueue.push

```python
push(self: Any, operation_id: str, connector: str, item_id: str, message: str)
```

Record a failed item operation.

---

#### SyncFailureQueue.replace_records

```python
replace_records(self: Any, entries: list[FailureRecord])
```

Replace queue entries with persisted state.

---

#### SyncFailureQueue.snapshot

```python
snapshot(self: Any)
```

Return all active failure records.

---

#### SyncFailureQueue.to_dict_list

```python
to_dict_list(self: Any)
```

Serialize active entries.

---

---

## SyncOperation

Record of a single sync operation.

### Methods

#### SyncOperation.to_dict

```python
to_dict(self: Any)
```

Convert to dictionary for JSON serialization.

---

---

## WorkstreamAutosyncAuthError

Authentication/authorization error.

**Inherits from**: `WorkstreamAutosyncError`

**Method Resolution Order**: `WorkstreamAutosyncAuthError -> WorkstreamAutosyncError`

---

## WorkstreamAutosyncConfig

Configuration for workstream autosync.

### Methods

#### WorkstreamAutosyncConfig.effective_github_project_number

```python
effective_github_project_number(self: Any)
```

Return effective GitHub project target (sandbox-aware).

---

#### WorkstreamAutosyncConfig.effective_partition_size

```python
effective_partition_size(self: Any)
```

Return a bounded partition size for planning.

---

#### WorkstreamAutosyncConfig.github_can_read

```python
github_can_read(self: Any)
```

Check if GitHub direction allows reading.

---

#### WorkstreamAutosyncConfig.github_can_write

```python
github_can_write(self: Any)
```

Check if GitHub direction allows writing.

---

#### WorkstreamAutosyncConfig.is_emergency_stop_active

```python
is_emergency_stop_active(self: Any)
```

Return whether emergency-stop controls are active.

---

#### WorkstreamAutosyncConfig.is_maintenance_active

```python
is_maintenance_active(self: Any, connector: str, at: Any, project: Any)
```

Return whether a connector is currently in planned maintenance.

---

#### WorkstreamAutosyncConfig.is_valid

```python
is_valid(self: Any)
```

Check if config has at least one platform enabled.

---

#### WorkstreamAutosyncConfig.linear_can_read

```python
linear_can_read(self: Any)
```

Check if Linear direction allows reading.

---

#### WorkstreamAutosyncConfig.linear_can_write

```python
linear_can_write(self: Any)
```

Check if Linear direction allows writing.

---

#### WorkstreamAutosyncConfig.matches_scope_filters

```python
matches_scope_filters(self: Any, item: WorkstreamItem)
```

Return whether a work item is included by configured sync scope filters.

---

#### WorkstreamAutosyncConfig.normalized_scope_areas

```python
normalized_scope_areas(self: Any)
```

---

#### WorkstreamAutosyncConfig.normalized_scope_priorities

```python
normalized_scope_priorities(self: Any)
```

---

#### WorkstreamAutosyncConfig.normalized_scope_statuses

```python
normalized_scope_statuses(self: Any)
```

---

#### WorkstreamAutosyncConfig.normalized_scope_wl_ranges

```python
normalized_scope_wl_ranges(self: Any)
```

---

#### WorkstreamAutosyncConfig.normalized_wl_ignore_list

```python
normalized_wl_ignore_list(self: Any)
```

Return canonical WL IDs to skip during sync cycles.

---

#### WorkstreamAutosyncConfig.should_sync_github

```python
should_sync_github(self: Any)
```

Check if GitHub sync is enabled and configured.

---

#### WorkstreamAutosyncConfig.should_sync_linear

```python
should_sync_linear(self: Any)
```

Check if Linear sync is enabled and configured.

---

---

## WorkstreamAutosyncConfigError

Configuration validation error.

**Inherits from**: `WorkstreamAutosyncError`

**Method Resolution Order**: `WorkstreamAutosyncConfigError -> WorkstreamAutosyncError`

---

## WorkstreamAutosyncError

Base exception for workstream autosync errors.

**Inherits from**: `Exception`

---

## WorkstreamAutosyncMaintenanceError

Raised when a maintenance window blocks sync operations.

**Inherits from**: `WorkstreamAutosyncError`

**Method Resolution Order**: `WorkstreamAutosyncMaintenanceError -> WorkstreamAutosyncError`

---

## WorkstreamDuplicateTitleError

Raised for duplicate workstream titles.

**Inherits from**: `WorkstreamAutosyncConfigError`

**Method Resolution Order**: `WorkstreamDuplicateTitleError -> WorkstreamAutosyncConfigError -> WorkstreamAutosyncError`

---

## WorkstreamItem

Parsed work stream item.

### Methods

#### WorkstreamItem.to_dict

```python
to_dict(self: Any)
```

Convert to dictionary for JSON serialization.

---

---

## WorkstreamParser

Parse WORK_STREAM.md and extract work items.

### Methods

#### WorkstreamParser.duplicate_titles

```python
duplicate_titles(cls: Any, items: list[WorkstreamItem])
```

Return duplicate titles mapped to item clusters.

---

#### WorkstreamParser.open_blocker_digest

```python
open_blocker_digest(cls: Any, items: list[WorkstreamItem])
```

Build a digest list for items still blocked by dependencies.

---

#### WorkstreamParser.parse_items

```python
parse_items(cls: Any, work_stream_path: Path)
```

Parse WORK_STREAM.md and extract work items.

**Parameters**:

- `work_stream_path`: Path to WORK_STREAM.md

**Returns**: List of parsed work items

---

#### WorkstreamParser.split_items

```python
split_items(cls: Any, items: list[WorkstreamItem], partition_size: int)
```

Split items into partitions by configured size.

---

#### WorkstreamParser.sync_sla_annotations

```python
sync_sla_annotations(cls: Any, text: str)
```

Ensure each SLA field is reflected in markdown content.

---

#### WorkstreamParser.sync_status_annotations

```python
sync_status_annotations(cls: Any, text: str)
```

Ensure status lines are synchronized from remote updates.

---

#### WorkstreamParser.validate_tags

```python
validate_tags(cls: Any, items: list[WorkstreamItem])
```

Validate local tag taxonomy against an allowed set.

---

---

## WorkstreamPartition

Partition for large sync ranges.

### Methods

#### WorkstreamPartition.count

```python
count(self: Any)
```

Return number of items in the partition.

---

---

## build_owner_metadata

```python
build_owner_metadata(owner: str)
```

Build canonical owner fields for local/GitHub/Linear propagation.

---

## compute_adaptive_sync_interval

Compute next-cycle interval from drift/error/load metrics.

Higher drift or error rates shrink the interval.
Higher load factor expands the interval to reduce pressure.

---

## count

```python
count(self: Any)
```

Return number of items in the partition.

---

## duplicate_titles

```python
duplicate_titles(cls: Any, items: list[WorkstreamItem])
```

Return duplicate titles mapped to item clusters.

---

## effective_github_project_number

```python
effective_github_project_number(self: Any)
```

Return effective GitHub project target (sandbox-aware).

---

## effective_partition_size

```python
effective_partition_size(self: Any)
```

Return a bounded partition size for planning.

---

## from_dict

```python
from_dict(cls: Any, payload: dict[(str, Any)])
```

Construct a checkpoint from serialized state.

---

## github_can_read

```python
github_can_read(self: Any)
```

Check if GitHub direction allows reading.

---

## github_can_write

```python
github_can_write(self: Any)
```

Check if GitHub direction allows writing.

---

## is_active

```python
is_active(self: Any, now: datetime)
```

Return whether the window is active at the given timestamp.

---

## is_emergency_stop_active

```python
is_emergency_stop_active(self: Any)
```

Return whether emergency-stop controls are active.

---

## is_maintenance_active

```python
is_maintenance_active(self: Any, connector: str, at: Any, project: Any)
```

Return whether a connector is currently in planned maintenance.

---

## is_valid

```python
is_valid(self: Any)
```

Check if config has at least one platform enabled.

---

## linear_can_read

```python
linear_can_read(self: Any)
```

Check if Linear direction allows reading.

---

## linear_can_write

```python
linear_can_write(self: Any)
```

Check if Linear direction allows writing.

---

## load_autosync_config_from_env

Load autosync configuration from environment variables.

Environment variables:
    THGENT_WORKSTREAM_AUTOSYNC_ENABLED: Enable autosync (true/false)
    THGENT_WORKSTREAM_AUTOSYNC_INTERVAL: Cycle interval in seconds (default: 300)
    THGENT_GITHUB_ENABLED: Enable GitHub sync (true/false)
    THGENT_GITHUB_OWNER: GitHub repository owner
    THGENT_GITHUB_PROJECT_NUMBER: GitHub project v2 number
THGENT_GITHUB_DIRECTION: Sync direction (read_only|write_only|bidirectional)
    THGENT_LINEAR_ENABLED: Enable Linear sync (true/false)
    THGENT_LINEAR_API_KEY: Linear API key
    THGENT_LINEAR_TEAM_KEY: Linear team key
THGENT_LINEAR_DIRECTION: Sync direction (read_only|write_only|bidirectional)
THGENT_WORKSTREAM_PATH: Path to WORK_STREAM.md
THGENT_AUTOSYNC_STATUS_PATH: Path to autosync status JSON
THGENT_WORKSTREAM_AUTOSYNC_CHECKPOINT_PATH: Path to checkpoint JSON
THGENT_WORKSTREAM_AUTOSYNC_MAX_PARTITION_SIZE: Dynamic partition size
THGENT_WORKSTREAM_AUTOSYNC_TTL_SECONDS: Checkpoint TTL seconds
THGENT_AUTOSYNC_MAINTENANCE_WINDOWS: Maintenance windows (`connector:start:end:project:reason` or `connector:start:end:reason` legacy; JSON array also supported)
THGENT_WORKSTREAM_TAG_TAXONOMY: Comma-separated approved tags
THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_PATH: Path to failure queue JSON
THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_TTL_SECONDS: Failure queue retention seconds
THGENT_WORKSTREAM_AUTOSYNC_CHANGE_DIGEST_PATH: Path for hourly change digest JSONL output
THGENT_WORKSTREAM_AUTOSYNC_REFLECTION_EVENT_LOG_PATH: Path for reflection event log JSONL output
THGENT_AUTOSYNC_CONNECTOR_SLA_THRESHOLDS: JSON connector SLA thresholds (`{"github":{"p95_latency_ms":250,"max_failure_rate":0.2}}`)
THGENT_WORKSTREAM_STRICT_TAG_VALIDATION: Require tags to match taxonomy
THGENT_WORKSTREAM_STRICT_TITLE_VALIDATION: Require duplicate titles to fail
THGENT_AUTOSYNC_EMERGENCY_STOP_ENABLED: Enable emergency stop checks
THGENT_AUTOSYNC_EMERGENCY_STOP_FILE_PATH: Sentinel file path for emergency stop
THGENT_AUTOSYNC_EMERGENCY_STOP_ENV_VAR: Env var name checked for emergency stop activation

**Returns**: WorkstreamAutosyncConfig instance

---

## matches_scope_filters

```python
matches_scope_filters(self: Any, item: WorkstreamItem)
```

Return whether a work item is included by configured sync scope filters.

---

## normalized_scope_areas

```python
normalized_scope_areas(self: Any) -> set[str]
```

---

## normalized_scope_priorities

```python
normalized_scope_priorities(self: Any) -> set[str]
```

---

## normalized_scope_statuses

```python
normalized_scope_statuses(self: Any) -> set[str]
```

---

## normalized_scope_wl_ranges

```python
normalized_scope_wl_ranges(self: Any) -> list[tuple[(int, int)]]
```

---

## normalized_wl_ignore_list

```python
normalized_wl_ignore_list(self: Any)
```

Return canonical WL IDs to skip during sync cycles.

---

## open_blocker_digest

```python
open_blocker_digest(cls: Any, items: list[WorkstreamItem])
```

Build a digest list for items still blocked by dependencies.

---

## parse_bool

```python
parse_bool(value: Any, default: bool) -> bool
```

---

## parse_bootstrap_mappings

```python
parse_bootstrap_mappings(raw: Any) -> list[str]
```

---

## parse_capability_map

```python
parse_capability_map(raw: Any) -> dict[(str, list[str])]
```

---

## parse_connector_health_states

```python
parse_connector_health_states(raw: Any) -> dict[(str, str)]
```

---

## parse_connector_sla_thresholds

```python
parse_connector_sla_thresholds(raw: Any) -> dict[(str, ConnectorSLAThresholds)]
```

---

## parse_float

```python
parse_float(value: Any, default: float) -> float
```

---

## parse_int

```python
parse_int(value: Any, default: int) -> int
```

---

## parse_items

```python
parse_items(cls: Any, work_stream_path: Path)
```

Parse WORK_STREAM.md and extract work items.

**Parameters**:

- `work_stream_path`: Path to WORK_STREAM.md

**Returns**: List of parsed work items

---

## parse_json_windows

```python
parse_json_windows(raw: Any) -> list[MaintenanceWindow]
```

---

## parse_scope_tokens

```python
parse_scope_tokens(raw: Any) -> list[str]
```

---

## parse_tag_taxonomy

```python
parse_tag_taxonomy(raw: Any) -> list[str]
```

---

## parse_wl_ignore_list

```python
parse_wl_ignore_list(raw: Any) -> list[str]
```

---

## prune_expired

```python
prune_expired(self: Any, now: Any)
```

Drop failures older than retention window.

---

## push

```python
push(self: Any, operation_id: str, connector: str, item_id: str, message: str)
```

Record a failed item operation.

---

## replace_records

```python
replace_records(self: Any, entries: list[FailureRecord])
```

Replace queue entries with persisted state.

---

## should_sync_github

```python
should_sync_github(self: Any)
```

Check if GitHub sync is enabled and configured.

---

## should_sync_linear

```python
should_sync_linear(self: Any)
```

Check if Linear sync is enabled and configured.

---

## snapshot

```python
snapshot(self: Any)
```

Return all active failure records.

---

## split_items

```python
split_items(cls: Any, items: list[WorkstreamItem], partition_size: int)
```

Split items into partitions by configured size.

---

## sync_sla_annotations

```python
sync_sla_annotations(cls: Any, text: str)
```

Ensure each SLA field is reflected in markdown content.

---

## sync_status_annotations

```python
sync_status_annotations(cls: Any, text: str)
```

Ensure status lines are synchronized from remote updates.

---

## to_dict

```python
to_dict(self: Any) -> dict[(str, Any)]
```

---

## to_dict_list

```python
to_dict_list(self: Any)
```

Serialize active entries.

---

## validate_env_profile_drift

```python
validate_env_profile_drift(profiles: dict[(str, dict[(str, str)])], required_keys: set[str], allowed_drift_keys: Any)
```

Validate required autosync keys are consistent across env profiles.

---

## validate_tags

```python
validate_tags(cls: Any, items: list[WorkstreamItem])
```

Validate local tag taxonomy against an allowed set.

---

## with_hash

```python
with_hash(self: Any)
```

Return a copy with deterministic manifest hash.

---

