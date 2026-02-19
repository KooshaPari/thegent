# relativistic API Reference

> **Source**: `src/thegent/discovery/relativistic.py`

WP-43001: Relativistic Clock Sync Protocol.
Simulates clock synchronization across agents located in different gravitational wells or moving
at high relative velocities. Adjusts for time dilation using Lorentz transformations.

---

## RelativisticClockSync

Manages time dilation compensation for interstellar agent coordination.

### Methods

#### RelativisticClockSync.__init__

```python
__init__(self, base_node)
```

#### RelativisticClockSync.add_peer

Register a peer with its physical parameters.

```python
add_peer(self, node)
```

#### RelativisticClockSync.calculate_dilation_factor

WP-43001: Calculate the time dilation factor (Gamma) for a peer.

```python
calculate_dilation_factor(self, peer_id)
```

#### RelativisticClockSync.sync_timestamp

Convert a remote timestamp to the local base node's time frame.

```python
sync_timestamp(self, peer_id, remote_ts)
```

---

## RelativisticNode

A node in the relativistic network.

---

## add_peer

Register a peer with its physical parameters.

```python
add_peer(self, node)
```

---

## calculate_dilation_factor

WP-43001: Calculate the time dilation factor (Gamma) for a peer.

```python
calculate_dilation_factor(self, peer_id)
```

---

## sync_timestamp

Convert a remote timestamp to the local base node's time frame.

```python
sync_timestamp(self, peer_id, remote_ts)
```

---

