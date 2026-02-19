# homomorphic API Reference

> **Source**: `src/thegent/security/homomorphic.py`

WP-24003: Homomorphic Encryption for Context.
Enables agents to perform computations on encrypted context data without decrypting it.
Protects sensitive context in multi-tenant shared memory environments.

---

## HomomorphicContext

Simulates Fully Homomorphic Encryption (FHE) for agent context.

### Methods

#### HomomorphicContext.__init__

```python
__init__(self)
```

#### HomomorphicContext.compute_on_encrypted

Perform an operation (e.g. search, count) on encrypted data without decrypting.

```python
compute_on_encrypted(self, ciphertext, operation)
```

#### HomomorphicContext.decrypt_result

Decrypt the result of a homomorphic computation.

```python
decrypt_result(self, ciphertext)
```

#### HomomorphicContext.encrypt_context

Encrypt context data into an FHE ciphertext.

```python
encrypt_context(self, data)
```

---

## compute_on_encrypted

Perform an operation (e.g. search, count) on encrypted data without decrypting.

```python
compute_on_encrypted(self, ciphertext, operation)
```

---

## decrypt_result

Decrypt the result of a homomorphic computation.

```python
decrypt_result(self, ciphertext)
```

---

## encrypt_context

Encrypt context data into an FHE ciphertext.

```python
encrypt_context(self, data)
```

---

