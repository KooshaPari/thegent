# artifacts API Reference

> **Source**: `src/thegent/maif/artifacts.py`

MAIF Action Artifacts implementation for thegent.

---

## MAIFArtifact

MAIF (Model-Aware Information Flow) action artifact.

Provides signed, immutable record of an agent action.

**Inherits from**: `BaseModel`

### Methods

#### MAIFArtifact.get_canonical_data

```python
get_canonical_data(self: Any)
```

Return canonical JSON representation for signing.

---

---

## generate_key_pair

Generate a new RSA key pair for MAIF signing.

---

## get_canonical_data

```python
get_canonical_data(self: Any)
```

Return canonical JSON representation for signing.

---

## sign_artifact

```python
sign_artifact(artifact: MAIFArtifact, private_key: rsa.RSAPrivateKey)
```

Sign artifact with RSA private key.

---

## verify_artifact

```python
verify_artifact(artifact: MAIFArtifact, public_key: rsa.RSAPublicKey)
```

Verify artifact signature.

---
