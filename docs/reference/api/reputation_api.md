# reputation API Reference

> **Source**: `src/thegent/economy/reputation.py`

WP-26003: Decentralized Reputation System.
Tracks agent performance and reliability across the global mesh.
Uses weighted feedback and consensus to build decentralized trust scores.

---

## ReputationEntry

A single reputation event for an agent.

**Inherits from**: `BaseModel`

---

## ReputationManager

Manages decentralized trust and reputation for mesh agents.

### Methods

#### ReputationManager.__init__

```python
__init__(self)
```

#### ReputationManager.get_reputation_report

Generate a detailed reputation report for an agent.

```python
get_reputation_report(self, agent_id)
```

#### ReputationManager.get_trust_score

Retrieve the current trust score for an agent.

```python
get_trust_score(self, agent_id)
```

#### ReputationManager.submit_rating

Submit a rating for an agent's performance on a task.

```python
submit_rating(self, agent_id, reviewer_id, task_id, rating, feedback)
```

---

## get_reputation_report

Generate a detailed reputation report for an agent.

```python
get_reputation_report(self, agent_id)
```

---

## get_trust_score

Retrieve the current trust score for an agent.

```python
get_trust_score(self, agent_id)
```

---

## submit_rating

Submit a rating for an agent's performance on a task.

```python
submit_rating(self, agent_id, reviewer_id, task_id, rating, feedback)
```

---

