# ethics_proof API Reference

> **Source**: `src/thegent/verification/ethics_proof.py`

WP-39002: Formal Proof of Ethical Alignment.

Provides mathematically-grounded proofs that agent actions align with constitutional ethics.

---

## EthicalProofGenerator

Generates formal ethical proofs.

### Methods

#### EthicalProofGenerator.generate

```python
generate(self: Any, action_id: str, aligned: bool, evidence: list[str])
```

Generate a formal proof for an action.

---

---

## EthicalProofVerifier

Verifies formal ethical proofs.

### Methods

#### EthicalProofVerifier.verify

```python
verify(self: Any, proof: FormalEthicalProof)
```

Verify the integrity and validity of the ethical proof.

---

---

## FormalEthicalProof

A formal, verifiable proof of ethical alignment.

**Inherits from**: `ProofOfAlignment`

---

## generate

```python
generate(self: Any, action_id: str, aligned: bool, evidence: list[str])
```

Generate a formal proof for an action.

---

## verify

```python
verify(self: Any, proof: FormalEthicalProof)
```

Verify the integrity and validity of the ethical proof.

---
