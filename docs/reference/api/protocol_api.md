# protocol API Reference

> **Source**: `src/thegent/discovery/p2p/protocol.py`

WP-13001: P2P Agent Discovery and Peer-to-Peer Orchestration.

---

## P2PDiscovery

Zeroconf-style discovery for agents on the local network.

### Methods

#### P2PDiscovery.__init__

```python
__init__(self, agent_id, port, capabilities)
```

#### P2PDiscovery.list_peers

Return list of active peers (seen in last 30s).

```python
list_peers(self)
```

#### P2PDiscovery.start

Start discovery and heartbeat threads.

```python
start(self)
```

#### P2PDiscovery.stop

```python
stop(self)
```

---

## PeerAgent

Metadata for a peer agent on the network.

**Inherits from**: `BaseModel`

---

## list_peers

Return list of active peers (seen in last 30s).

```python
list_peers(self)
```

---

## start

Start discovery and heartbeat threads.

```python
start(self)
```

---

## stop

```python
stop(self)
```

---

