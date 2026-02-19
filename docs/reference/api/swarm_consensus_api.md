# swarm_consensus API Reference

> **Source**: `src/thegent/orchestration/swarm_consensus.py`

WP-24001: Swarm Consensus Protocol (Byzantine).
Ensures agreement on task outcomes across a swarm of autonomous agents.
Uses a simplified Byzantine Fault Tolerance (BFT) pattern.

---

## SwarmConsensus

Orchestrates consensus across multiple swarm agents.

### Methods

#### SwarmConsensus.__init__

```python
__init__(self, task_id, threshold)
```

#### SwarmConsensus.evaluate_consensus

Evaluate if consensus has been reached based on the threshold.

```python
evaluate_consensus(self, total_agents)
```

#### SwarmConsensus.get_audit_trail

Generate a cryptographic audit trail for the consensus process.

```python
get_audit_trail(self)
```

#### SwarmConsensus.record_vote

Record a vote from an agent in the swarm.

```python
record_vote(self, agent_id, vote, signature)
```

---

## SwarmVote

A single agent's vote on a task outcome.

**Inherits from**: `BaseModel`

---

## evaluate_consensus

Evaluate if consensus has been reached based on the threshold.

```python
evaluate_consensus(self, total_agents)
```

---

## get_audit_trail

Generate a cryptographic audit trail for the consensus process.

```python
get_audit_trail(self)
```

---

## record_vote

Record a vote from an agent in the swarm.

```python
record_vote(self, agent_id, vote, signature)
```

---

