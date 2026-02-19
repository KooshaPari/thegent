# quantum_safe API Reference

> **Source**: `src/thegent/security/quantum_safe.py`

WP-24001: Post-Quantum Cryptographic (PQC) Signatures.
Ensures that agent artifacts are signed using algorithms resistant to quantum computer attacks.
Uses NIST-selected candidates like Dilithium or Falcon (Simulated).

---

## PQCSigner

Provides quantum-resistant digital signatures for agent artifacts.

### Methods

#### PQCSigner.__init__

```python
__init__(self, algorithm)
```

#### PQCSigner.sign_artifact

Sign artifact data using the PQC private key.

```python
sign_artifact(self, artifact_data)
```

#### PQCSigner.verify_signature

Verify a PQC signature.

```python
verify_signature(self, artifact_data, signature, public_key)
```

---

## sign_artifact

Sign artifact data using the PQC private key.

```python
sign_artifact(self, artifact_data)
```

---

## verify_signature

Verify a PQC signature.

```python
verify_signature(self, artifact_data, signature, public_key)
```

---

