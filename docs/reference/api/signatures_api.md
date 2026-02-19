# signatures API Reference

> **Source**: `src/thegent/governance/signatures.py`

WP-3002: Signed action artifacts and provenance signatures (FR-010).

BKM-03: When THGENT_USE_NATIVE_CRYPTO=1, uses thegent_crypto Rust extension
for hash/sign/verify. Falls back to Python hashlib/hmac otherwise.

---

## ArtifactSigner

Manager for signing and verifying governance artifacts.

### Methods

#### ArtifactSigner.__init__

```python
__init__(self, settings)
```

#### ArtifactSigner.create_signed_artifact

Create a signed artifact with metadata.

```python
create_signed_artifact(self, artifact_type, payload)
```

#### ArtifactSigner.verify_envelope

Verify the signature of an artifact envelope.

```python
verify_envelope(self, envelope)
```

---

## create_signed_artifact

Create a signed artifact with metadata.

```python
create_signed_artifact(self, artifact_type, payload)
```

---

## generate_artifact_hash

Generate SHA-256 hash of a dictionary artifact.

```python
generate_artifact_hash(data)
```

---

## sign_artifact

Produce a provenance signature for an artifact using HMAC-SHA256.

```python
sign_artifact(data, secret_key)
```

---

## verify_envelope

Verify the signature of an artifact envelope.

```python
verify_envelope(self, envelope)
```

---

## verify_signature

Verify the provenance signature of an artifact.

```python
verify_signature(data, signature, secret_key)
```

---

