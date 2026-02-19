# mesh API Reference

> **Source**: `src/thegent/discovery/mesh.py`

WP-26001: Global Mesh Networking for Agents.
Extends agent discovery beyond the local network using a global mesh protocol.
Inspired by libp2p and Tailscale-style overlay networking.

---

## AgentMesh

Manages global agent connectivity and peer discovery.

### Methods

#### AgentMesh.__init__

```python
__init__(self, node_id, registry_url)
```

#### AgentMesh.discover_peers

Discover peers in the global mesh with specific capabilities.

```python
discover_peers(self, capability)
```

#### AgentMesh.join_mesh

Register the local agent with the global mesh registry.

```python
join_mesh(self, public_addr)
```

#### AgentMesh.route_to_peer

Route a message payload over the mesh overlay network.

```python
route_to_peer(self, peer_id, payload)
```

---

## MeshNode

Metadata for a node in the global agent mesh.

**Inherits from**: `BaseModel`

---

## discover_peers

Discover peers in the global mesh with specific capabilities.

```python
discover_peers(self, capability)
```

---

## join_mesh

Register the local agent with the global mesh registry.

```python
join_mesh(self, public_addr)
```

---

## route_to_peer

Route a message payload over the mesh overlay network.

```python
route_to_peer(self, peer_id, payload)
```

---

