# consensus API Reference

> **Source**: `src/thegent/mesh/consensus.py`

Consensus and escalation protocols for the agent mesh.

---

## CausalInfluenceTracker

Shapley-value causal influence tracking (SCLI-P3.2).

### Methods

#### CausalInfluenceTracker.__init__

```python
__init__(self: Any, mesh_root: Path)
```

---

#### CausalInfluenceTracker.compute_shapley_values

```python
compute_shapley_values(self: Any, action_id: str)
```

Compute per-agent causal influence using Shapley-style normalized attribution.

---

#### CausalInfluenceTracker.record_influence

```python
record_influence(self: Any, agent_id: str, action_id: str, contribution: float)
```

Log contribution for later analysis.

---

---

## ConsensusProtocol

Crash-Preventing Weighted Byzantine Fault Tolerance (CP-WBFT) (ADR-013, SCLI-P3.1).

### Methods

#### ConsensusProtocol.__init__

```python
__init__(self: Any, mesh_root: Path)
```

---

#### ConsensusProtocol.advance_debate_round

```python
advance_debate_round(self: Any, proposal_id: str)
```

Move a proposal to the next debate round, capped by configured max rounds.

---

#### ConsensusProtocol.cast_vote

```python
cast_vote(self: Any, proposal_id: str, agent_id: str, vote: bool, confidence: float, vote_round: int)
```

Phase 4: VOTE (ADR-013). Cast a weighted vote for the finalized proposal.

---

#### ConsensusProtocol.draft

```python
draft(self: Any, proposal_id: str, agent_id: str, refinement: dict)
```

Phase 2: DRAFT (ADR-013). Agents can provide refinements or counter-proposals.

---

#### ConsensusProtocol.get_consensus

```python
get_consensus(self: Any, proposal_id: str, required_majority: Any, vote_round: Any)
```

Phase 5 & 6: TALLY & DECIDE (ADR-013). Check if consensus is reached.

---

#### ConsensusProtocol.propose

```python
propose(self: Any, proposal_id: str, agent_id: str, topic: str, content: dict, decision_type: str, max_debate_rounds: int)
```

Phase 1: PROPOSE (ADR-013). Initial proposal by a leader.

---

#### ConsensusProtocol.share

```python
share(self: Any, proposal_id: str)
```

Phase 3: SHARE (ADR-013). Finalize the proposal after drafting period.

---

---

## ConsensusStatus

**Inherits from**: `enum.Enum`

---

## EscalationWorkflow

5-tier escalation workflow (SCLI-P3.3).

### Methods

#### EscalationWorkflow.__init__

```python
__init__(self: Any, mesh_root: Path)
```

---

#### EscalationWorkflow.escalate

```python
escalate(self: Any, proposal_id: str, current_tier: int, reason: str, metadata: Any)
```

Escalate to next tier (SCLI-P3.3).

---

#### EscalationWorkflow.list_pending_human_escalations

```python
list_pending_human_escalations(self: Any)
```

List pending asynchronous human escalations (SCLI-P3.4).

---

#### EscalationWorkflow.resolve_human_escalation

```python
resolve_human_escalation(self: Any, proposal_id: str, status: str)
```

Resolve a queued human escalation item.

---

---

## advance_debate_round

```python
advance_debate_round(self: Any, proposal_id: str)
```

Move a proposal to the next debate round, capped by configured max rounds.

---

## cast_vote

```python
cast_vote(self: Any, proposal_id: str, agent_id: str, vote: bool, confidence: float, vote_round: int)
```

Phase 4: VOTE (ADR-013). Cast a weighted vote for the finalized proposal.

---

## compute_shapley_values

```python
compute_shapley_values(self: Any, action_id: str)
```

Compute per-agent causal influence using Shapley-style normalized attribution.

---

## draft

```python
draft(self: Any, proposal_id: str, agent_id: str, refinement: dict)
```

Phase 2: DRAFT (ADR-013). Agents can provide refinements or counter-proposals.

---

## escalate

```python
escalate(self: Any, proposal_id: str, current_tier: int, reason: str, metadata: Any)
```

Escalate to next tier (SCLI-P3.3).

---

## get_consensus

```python
get_consensus(self: Any, proposal_id: str, required_majority: Any, vote_round: Any)
```

Phase 5 & 6: TALLY & DECIDE (ADR-013). Check if consensus is reached.

---

## list_pending_human_escalations

```python
list_pending_human_escalations(self: Any)
```

List pending asynchronous human escalations (SCLI-P3.4).

---

## propose

```python
propose(self: Any, proposal_id: str, agent_id: str, topic: str, content: dict, decision_type: str, max_debate_rounds: int)
```

Phase 1: PROPOSE (ADR-013). Initial proposal by a leader.

---

## record_influence

```python
record_influence(self: Any, agent_id: str, action_id: str, contribution: float)
```

Log contribution for later analysis.

---

## resolve_human_escalation

```python
resolve_human_escalation(self: Any, proposal_id: str, status: str)
```

Resolve a queued human escalation item.

---

## share

```python
share(self: Any, proposal_id: str)
```

Phase 3: SHARE (ADR-013). Finalize the proposal after drafting period.

---

