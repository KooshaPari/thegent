# digital_twin API Reference

> **Source**: `src/thegent/agents/digital_twin.py`

WP-41003: Legacy Identity Preservation (Digital Twin).
Maintains a persistent, evolving digital twin of a human user or agent persona.
Ensures continuity of 'intent' and 'values' across different hardware or model migrations.

---

## DigitalTwinManager

Manages the creation and synchronization of digital identity twins.

### Methods

#### DigitalTwinManager.__init__

```python
__init__(self, storage_dir)
```

#### DigitalTwinManager.capture_snapshot

WP-41003: Capture the current state of a persona for preservation.

```python
capture_snapshot(self, identity_id, values)
```

#### DigitalTwinManager.reconcile_twin

Merge traits from two snapshots (e.g. from different project instances).

```python
reconcile_twin(self, twin_a_id, twin_b_id)
```

---

## PersonaSnapshot

A point-in-time snapshot of an identity's values and memory.

---

## capture_snapshot

WP-41003: Capture the current state of a persona for preservation.

```python
capture_snapshot(self, identity_id, values)
```

---

## reconcile_twin

Merge traits from two snapshots (e.g. from different project instances).

```python
reconcile_twin(self, twin_a_id, twin_b_id)
```

---

