# encryption_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/encryption_adapter.py`

Encryption adapter for workstream autosync.

Handles artifact encryption/decryption using XOR cipher.

---

## compute_artifact_key

```python
compute_artifact_key(actor_id: str, artifact_id: str)
```

Compute encryption key for artifact.

**Parameters**:

- `actor_id`: Actor identifier
- `artifact_id`: Artifact identifier

**Returns**: Encryption key string

---

## xor_decrypt

```python
xor_decrypt(payload: str, key: str)
```

Decrypt XOR-encrypted payload.

**Parameters**:

- `payload`: Base64-encoded encrypted string
- `key`: Encryption key string

**Returns**: Decrypted string

---

## xor_encrypt

```python
xor_encrypt(data: bytes, key: str)
```

Encrypt data using XOR cipher with key.

**Parameters**:

- `data`: Raw bytes to encrypt
- `key`: Encryption key string

**Returns**: Base64-encoded encrypted string

---

