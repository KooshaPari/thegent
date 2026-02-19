# load_based_limits API Reference

> **Source**: `src/thegent/orchestration/load_based_limits.py`

WP-5001: Load-based concurrency limits (FD, memory, CPU, load average).

Replaces fixed max_concurrency with dynamic, resource-aware limits that scale
as a load balancer: allow more slots when system headroom exists, throttle when
gates are near capacity.

BKM-04: When THGENT_USE_NATIVE_RESOURCES=1, uses thegent-resources Rust binary
instead of lsof/vm_stat subprocesses. Set THGENT_RESOURCES_BIN to override path.

---

## HysteresisController

WP-Y6: Prevents thrashing by using upper/lower thresholds and dwell time.

### Methods

#### HysteresisController.__init__

```python
__init__(self, upper_threshold, lower_threshold, dwell_time_s)
```

#### HysteresisController.get_limit

Apply hysteresis to determine the new limit.
Returns the new limit (either changed or held).

```python
get_limit(self, current_limit, running_count, target_limit)
```

---

## LimitGateConfig

Configuration for each resource gate. Thresholds are 0.0–1.0 (utilization).

### Methods

#### LimitGateConfig.from_dict

Build config from dict (e.g. settings).

```python
from_dict(cls, d)
```

---

## ResourceSnapshot

Current system resource usage for limit calculation.

---

## compute_dynamic_limit

Compute max concurrent slots from resource gates. Load-balancer style:
scale up when headroom exists, throttle when any gate is near capacity.

Returns (effective_limit, gate_details).

```python
compute_dynamic_limit(snapshot, config, running_count)
```

---

## from_dict

Build config from dict (e.g. settings).

```python
from_dict(cls, d)
```

---

## get_limit

Apply hysteresis to determine the new limit.
Returns the new limit (either changed or held).

```python
get_limit(self, current_limit, running_count, target_limit)
```

---

## sample_resources

Sample current system resources. Cross-platform where possible.

Uses thegent-resources Rust binary when THGENT_USE_NATIVE_RESOURCES=1;
otherwise falls back to Python (lsof/vm_stat on macOS, /proc on Linux).

---

