# edge_sync API Reference

> **Source**: `src/thegent/discovery/edge_sync.py`

WP-40003: Edge-Agent Low-Power Synchronization.
Enables agents running on constrained edge devices (IoT, Mobile) to synchronize state
using delta-compression and adaptive polling to conserve energy.

---

## EdgeSyncController

Manages low-power synchronization between edge agents and the mesh.

### Methods

#### EdgeSyncController.__init__

```python
__init__(self, device_id)
```

#### EdgeSyncController.apply_remote_delta

Apply a received delta to the local base state.

```python
apply_remote_delta(self, compressed_delta)
```

#### EdgeSyncController.compute_delta

WP-40003: Generate a compressed delta between base and current state.

```python
compute_delta(self, current_state)
```

#### EdgeSyncController.get_adaptive_polling_interval

Adjust sync frequency based on battery (0.0 - 1.0).

```python
get_adaptive_polling_interval(self, battery_level)
```

---

## apply_remote_delta

Apply a received delta to the local base state.

```python
apply_remote_delta(self, compressed_delta)
```

---

## compute_delta

WP-40003: Generate a compressed delta between base and current state.

```python
compute_delta(self, current_state)
```

---

## get_adaptive_polling_interval

Adjust sync frequency based on battery (0.0 - 1.0).

```python
get_adaptive_polling_interval(self, battery_level)
```

---

