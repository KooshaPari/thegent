# zkp API Reference

> **Source**: `src/thegent/verification/zkp.py`

WP-27002: Zero-Knowledge Proofs (ZKP) for Context Integrity.
Enables agents to prove they have certain context or permissions without revealing the raw data.
Uses a simplified ZK-SNARK-inspired pattern for agent governance.

---

## ZKGovernor

Orchestrates Zero-Knowledge governance for sensitive context.

### Methods

#### ZKGovernor.__init__

```python
__init__(self, agent_id)
```

#### ZKGovernor.generate_proof

Generate a ZK proof for a given secret context and challenge.

```python
generate_proof(self, secret_context, challenge)
```

#### ZKGovernor.verify_proof

Verify a ZK proof against a known commitment.

```python
verify_proof(self, proof, known_commitment)
```

---

## ZKProof

Metadata for a Zero-Knowledge Proof.

**Inherits from**: `BaseModel`

---

## generate_proof

Generate a ZK proof for a given secret context and challenge.

```python
generate_proof(self, secret_context, challenge)
```

---

## verify_proof

Verify a ZK proof against a known commitment.

```python
verify_proof(self, proof, known_commitment)
```

---

