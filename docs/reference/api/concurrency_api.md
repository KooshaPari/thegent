# concurrency API Reference

> **Source**: `src/thegent/execution/concurrency.py`

Execution run metadata and registry for thegent orchestration.

---

## ConcurrencyController

WP-5001: Advanced resource-based adaptive concurrency controller.

Features:
- Extended resource indices (CPU, memory, FD, network, disk, GPU, etc.)
- Prediction engine for forecasting resource needs
- Harness card modeling (codex/claude/droid usage profiles)
- Bottleneck detection and analysis
- Speculative execution strategies
- Work chunking and parallelization
- Per-owner usage tracking for fairness enforcement (swarm-usage-tracking)

### Methods

#### ConcurrencyController.__init__

```python
__init__(self: Any, session_dir: Path, max_concurrency: int, use_load_based: bool, critical_lane_slots: Any)
```

---

#### ConcurrencyController.acquire

```python
acquire(self: Any, lane: str, harness_type: Any, priority: str, owner: str, run_id: str, soft_deadline_s: Any, warn_at_pct: float, speculative: bool)
```

Acquire a concurrency slot using advanced resource-based limits.

Uses:
- Extended resource monitoring (CPU, memory, FD, network, disk, etc.)
- Prediction engine for forecasting
- Harness card modeling for harness-specific limits
- Bottleneck detection
- 5% minimum buffer (hard limit, prevents crashes)
- 15% discretionary buffer (soft limit, allows scaling)
- Critical lane reservation: standard runs are blocked from the top
  ``critical_lane_slots`` slots so that critical runs always find room.
- Per-owner usage tracking: records start when admitted.
- Soft deadline monitoring: registers a preferred completion time with
  the :class:`DeadlineMonitor` when ``soft_deadline_s`` is provided.
  Past-deadline runs are logged but never cancelled.

**Parameters**:

- `lane`: Lane name (``"standard"``, ``"critical"``, etc.).
- `harness_type`: Optional harness type for capacity modeling.
- `priority`: ``"critical"`` or ``"standard"`` (default).  A run is
treated as critical when ``priority="critical"`` OR when
``lane="critical"``.  Critical runs may use all available
slots; standard runs are limited to
``effective_limit - critical_lane_slots``.
- `owner`: Identifier for the owning agent/user/project (for fairness tracking).
- `run_id`: Unique run identifier (for tracing in usage logs).
- `soft_deadline_s`: Optional preferred completion budget in seconds.
When provided and the run is admitted, a soft deadline is
registered with the module-level :class:`DeadlineMonitor`.
Violations emit WARNING (at ``warn_at_pct * soft_deadline_s``)
and ERROR (at ``soft_deadline_s``) but do NOT cancel the run.
- `warn_at_pct`: Fraction of ``soft_deadline_s`` at which to warn
(default 0.8 → 80 %).  Only used when ``soft_deadline_s`` is set.

---

#### ConcurrencyController.get_bottlenecks

```python
get_bottlenecks(self: Any)
```

Get current bottlenecks and slow points.

---

#### ConcurrencyController.get_usage_stats

```python
get_usage_stats(self: Any)
```

Return per-owner usage statistics as a serializable dict.

Returns a mapping of ``{owner: stats_dict}`` suitable for CLI/MCP display.
Each value is the output of :meth:`OwnerStats.to_dict`.

---

#### ConcurrencyController.release

```python
release(self: Any, owner: str, run_id: str, elapsed_ms: float)
```

Record the completion of a run for per-owner usage tracking.

Also unregisters any soft deadline that was associated with this run so
that the :class:`DeadlineMonitor` stops checking it.

Call this after a run finishes (succeeded or failed) to decrement the
owner's active count and accumulate elapsed time statistics.

**Parameters**:

- `owner`:      Identifier used in the corresponding :meth:`acquire` call.
- `run_id`:     Run identifier used in the corresponding :meth:`acquire` call.
- `elapsed_ms`: Wall-clock duration of the run in milliseconds.

---

---

## IdempotencyManager

WP-1003: Ensures idempotent execution using 4-tuple keys.

### Methods

#### IdempotencyManager.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### IdempotencyManager.check_and_record

```python
check_and_record(self: Any, registry: RunRegistry, key: str)
```

Check if key exists in registry; return True if already executed.

---

#### IdempotencyManager.generate_key

```python
generate_key(self: Any, run_id: str, step_index: int, action_type: str, content: str)
```

Generate a 4-tuple idempotency key (run_id, step, action, hash).

---

---

## LaneController

WP-1002: Priority and urgency lane model for task management.

### Methods

#### LaneController.__init__

```python
__init__(self: Any, session_dir: Path, capacity: int)
```

---

#### LaneController.check_capacity

```python
check_capacity(self: Any, lane: str)
```

Check if a lane has capacity to run (starvation prevention).

---

#### LaneController.get_lane_priority

```python
get_lane_priority(self: Any, lane: str)
```

Return numeric priority for a lane (lower is higher priority).

---

#### LaneController.sort_tasks

```python
sort_tasks(self: Any, tasks: list[dict[(str, Any)]])
```

Sort tasks by lane priority and then by creation time.

---

---

## LoadClassifier

WP-5002: Classifies system load and detects burst conditions.

### Methods

#### LoadClassifier.__init__

```python
__init__(self: Any, session_dir: Path, spike_threshold: Any, surge_threshold: Any)
```

---

#### LoadClassifier.get_load_level

```python
get_load_level(self: Any)
```

Return current load level: normal, high, burst.

Uses resource-based thresholds when load-based limits are enabled:
- Normal: Below 70% of resource-based limit
- High: 70-95% of resource-based limit (15% discretionary buffer)
- Burst: Above 95% of resource-based limit (5% minimum buffer)

---

#### LoadClassifier.get_running_count

```python
get_running_count(self: Any)
```

Return count of currently running sessions.

---

#### LoadClassifier.get_traffic_shape

```python
get_traffic_shape(self: Any)
```

Return current traffic shape (normal, shaped, restricted).

---

#### LoadClassifier.is_safe_mode_active

```python
is_safe_mode_active(self: Any)
```

Return True if system is in safe-mode (burst load).

---

---

## acquire

```python
acquire(self: Any, lane: str, harness_type: Any, priority: str, owner: str, run_id: str, soft_deadline_s: Any, warn_at_pct: float, speculative: bool)
```

Acquire a concurrency slot using advanced resource-based limits.

Uses:
- Extended resource monitoring (CPU, memory, FD, network, disk, etc.)
- Prediction engine for forecasting
- Harness card modeling for harness-specific limits
- Bottleneck detection
- 5% minimum buffer (hard limit, prevents crashes)
- 15% discretionary buffer (soft limit, allows scaling)
- Critical lane reservation: standard runs are blocked from the top
  ``critical_lane_slots`` slots so that critical runs always find room.
- Per-owner usage tracking: records start when admitted.
- Soft deadline monitoring: registers a preferred completion time with
  the :class:`DeadlineMonitor` when ``soft_deadline_s`` is provided.
  Past-deadline runs are logged but never cancelled.

**Parameters**:

- `lane`: Lane name (``"standard"``, ``"critical"``, etc.).
- `harness_type`: Optional harness type for capacity modeling.
- `priority`: ``"critical"`` or ``"standard"`` (default).  A run is
treated as critical when ``priority="critical"`` OR when
``lane="critical"``.  Critical runs may use all available
slots; standard runs are limited to
``effective_limit - critical_lane_slots``.
- `owner`: Identifier for the owning agent/user/project (for fairness tracking).
- `run_id`: Unique run identifier (for tracing in usage logs).
- `soft_deadline_s`: Optional preferred completion budget in seconds.
When provided and the run is admitted, a soft deadline is
registered with the module-level :class:`DeadlineMonitor`.
Violations emit WARNING (at ``warn_at_pct * soft_deadline_s``)
and ERROR (at ``soft_deadline_s``) but do NOT cancel the run.
- `warn_at_pct`: Fraction of ``soft_deadline_s`` at which to warn
(default 0.8 → 80 %).  Only used when ``soft_deadline_s`` is set.

---

## check_and_record

```python
check_and_record(self: Any, registry: RunRegistry, key: str)
```

Check if key exists in registry; return True if already executed.

---

## check_capacity

```python
check_capacity(self: Any, lane: str)
```

Check if a lane has capacity to run (starvation prevention).

---

## generate_key

```python
generate_key(self: Any, run_id: str, step_index: int, action_type: str, content: str)
```

Generate a 4-tuple idempotency key (run_id, step, action, hash).

---

## get_bottlenecks

```python
get_bottlenecks(self: Any)
```

Get current bottlenecks and slow points.

---

## get_execution_diagnostics

Return diagnostics snapshot for execution-path degradation.

---

## get_lane_priority

```python
get_lane_priority(self: Any, lane: str)
```

Return numeric priority for a lane (lower is higher priority).

---

## get_load_level

```python
get_load_level(self: Any)
```

Return current load level: normal, high, burst.

Uses resource-based thresholds when load-based limits are enabled:
- Normal: Below 70% of resource-based limit
- High: 70-95% of resource-based limit (15% discretionary buffer)
- Burst: Above 95% of resource-based limit (5% minimum buffer)

---

## get_running_count

```python
get_running_count(self: Any)
```

Return count of currently running sessions.

---

## get_traffic_shape

```python
get_traffic_shape(self: Any)
```

Return current traffic shape (normal, shaped, restricted).

---

## get_usage_stats

```python
get_usage_stats(self: Any)
```

Return per-owner usage statistics as a serializable dict.

Returns a mapping of ``{owner: stats_dict}`` suitable for CLI/MCP display.
Each value is the output of :meth:`OwnerStats.to_dict`.

---

## is_safe_mode_active

```python
is_safe_mode_active(self: Any)
```

Return True if system is in safe-mode (burst load).

---

## release

```python
release(self: Any, owner: str, run_id: str, elapsed_ms: float)
```

Record the completion of a run for per-owner usage tracking.

Also unregisters any soft deadline that was associated with this run so
that the :class:`DeadlineMonitor` stops checking it.

Call this after a run finishes (succeeded or failed) to decrement the
owner's active count and accumulate elapsed time statistics.

**Parameters**:

- `owner`:      Identifier used in the corresponding :meth:`acquire` call.
- `run_id`:     Run identifier used in the corresponding :meth:`acquire` call.
- `elapsed_ms`: Wall-clock duration of the run in milliseconds.

---

## reset_execution_diagnostics

Reset execution diagnostics (test helper).

---

## sort_tasks

```python
sort_tasks(self: Any, tasks: list[dict[(str, Any)]])
```

Sort tasks by lane priority and then by creation time.

---

