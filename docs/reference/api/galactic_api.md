# galactic API Reference

> **Source**: `src/thegent/discovery/galactic.py`

WP-34001: Delay-Tolerant Networking (DTN) Bridge.
Enables agent communication over high-latency, intermittently connected links (Inter-Galactic).
Inspired by NASA's DTN (BPv7) protocols.

---

## Bundle

A DTN Bundle (data packet) for long-delay transport.

---

## DTNBridge

Bridges standard thegent networking with Delay-Tolerant protocols.

### Methods

#### DTNBridge.__init__

```python
__init__(self, node_id)
```

#### DTNBridge.add_contact

Schedule a future contact opportunity.

```python
add_contact(self, node_id, contact_time)
```

#### DTNBridge.process_contacts

WP-34002: Reconcile state when contact is established.

```python
process_contacts(self)
```

#### DTNBridge.send_bundle

Queue a bundle for transmission.

```python
send_bundle(self, dest_node, payload)
```

---

## add_contact

Schedule a future contact opportunity.

```python
add_contact(self, node_id, contact_time)
```

---

## process_contacts

WP-34002: Reconcile state when contact is established.

```python
process_contacts(self)
```

---

## send_bundle

Queue a bundle for transmission.

```python
send_bundle(self, dest_node, payload)
```

---

