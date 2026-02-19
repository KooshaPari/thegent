# ethics_proof API Reference

> **Source**: `src/thegent/verification/ethics_proof.py`

WP-39002: Formal Proof of Ethical Alignment.
Provides mathematically-grounded proofs that agent actions align with constitutional ethics.

---

## EthicalProofGenerator

Generates formal ethical proofs.

### Methods

#### EthicalProofGenerator.generate

Generate a formal proof for an action.

```python
generate(self, action_id, aligned, evidence)
```

---

## EthicalProofVerifier

Verifies formal ethical proofs.

### Methods

#### EthicalProofVerifier.verify

Verify the integrity and validity of the ethical proof.

```python
verify(self, proof)
```

---

## FormalEthicalProof

A formal, verifiable proof of ethical alignment.

**Inherits from**: `ProofOfAlignment`

---

## generate

Generate a formal proof for an action.

```python
generate(self, action_id, aligned, evidence)
```

---

## verify

Verify the integrity and validity of the ethical proof.

```python
verify(self, proof)
```

---

