# omega_consensus API Reference

> **Source**: `src/thegent/orchestration/omega_consensus.py`

WP-45003: Final State Consensus Protocol (Omega).
Ensures all agents in the swarm agree on the final project state using BFT.

---

## OmegaConsensus

The final consensus engine for thegent (Phase 45).
Enforces agreement on the project's 'Omega' (final) state across all agents.

### Methods

#### OmegaConsensus.__init__

```python
__init__(self, swarm_size, threshold)
```

#### OmegaConsensus.cast_vote

Cast a vote for an Omega proposal.

```python
cast_vote(self, proposal_id, voter_id, vote, signature)
```

#### OmegaConsensus.finalize_consensus

Check if a proposal has reached consensus and finalize the state.

```python
finalize_consensus(self, proposal_id)
```

#### OmegaConsensus.get_final_state

Return the finalized Omega state if consensus was reached.

```python
get_final_state(self)
```

#### OmegaConsensus.propose_state

Propose a new final state for the project.

```python
propose_state(self, proposer_id, state, metadata)
```

---

## OmegaProposal

A proposal for the final state of the project.

**Inherits from**: `BaseModel`

---

## OmegaVote

A vote on an Omega proposal.

**Inherits from**: `BaseModel`

---

## cast_vote

Cast a vote for an Omega proposal.

```python
cast_vote(self, proposal_id, voter_id, vote, signature)
```

---

## finalize_consensus

Check if a proposal has reached consensus and finalize the state.

```python
finalize_consensus(self, proposal_id)
```

---

## get_final_state

Return the finalized Omega state if consensus was reached.

```python
get_final_state(self)
```

---

## propose_state

Propose a new final state for the project.

```python
propose_state(self, proposer_id, state, metadata)
```

---

