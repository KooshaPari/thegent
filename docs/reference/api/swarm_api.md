# swarm API Reference

> **Source**: `src/thegent/orchestration/swarm.py`

Swarm coordination and shared memory for thegent (WP-1006).

---

## ACLMessage

WP-1006: JSON-ACL Message for inter-agent communication.

**Inherits from**: `BaseModel`

---

## Blackboard

WP-1006: Shared memory for multi-agent coordination.

### Methods

#### Blackboard.__init__

```python
__init__(self, namespace)
```

#### Blackboard.list_keys

List all keys on the blackboard.

```python
list_keys(self)
```

#### Blackboard.post

Post a finding or result to the blackboard.

```python
post(self, key, value)
```

#### Blackboard.read

Read a value from the blackboard.

```python
read(self, key)
```

---

## ConsensusManager

WP-1006: Resolves conflicts when multiple agents propose solutions.

### Methods

#### ConsensusManager.resolve_by_confidence

Pick the proposal with the highest confidence score.

```python
resolve_by_confidence(proposals)
```

#### ConsensusManager.resolve_by_vote

Majority vote on identical proposal values.

```python
resolve_by_vote(proposals)
```

---

## NegotiationEngine

WP-1006: Handles inter-agent negotiation and Nash Equilibrium selection.

### Methods

#### NegotiationEngine.__init__

```python
__init__(self, blackboard)
```

#### NegotiationEngine.resolve_conflict

Find the optimal proposal using utility scores.

```python
resolve_conflict(self, proposals)
```

---

## list_keys

List all keys on the blackboard.

```python
list_keys(self)
```

---

## post

Post a finding or result to the blackboard.

```python
post(self, key, value)
```

---

## read

Read a value from the blackboard.

```python
read(self, key)
```

---

## resolve_by_confidence

Pick the proposal with the highest confidence score.

```python
resolve_by_confidence(proposals)
```

---

## resolve_by_vote

Majority vote on identical proposal values.

```python
resolve_by_vote(proposals)
```

---

## resolve_conflict

Find the optimal proposal using utility scores.

```python
resolve_conflict(self, proposals)
```

---

