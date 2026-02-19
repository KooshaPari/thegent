# marketplace API Reference

> **Source**: `src/thegent/contracts/marketplace.py`

WP-15003: Enterprise plugin marketplace contracts with RSA verification.

---

## PluginContract

---

## PluginVerifier

Verifies third-party plugin contracts for safe execution (WP-15003).

### Methods

#### PluginVerifier.__init__

```python
__init__(self, public_key_dir)
```

#### PluginVerifier.check_permissions

Check if the plugin contract allows the requested action.

```python
check_permissions(self, contract, requested_action)
```

#### PluginVerifier.verify_contract

Verify the signature of a plugin contract.

```python
verify_contract(self, contract)
```

---

## check_permissions

Check if the plugin contract allows the requested action.

```python
check_permissions(self, contract, requested_action)
```

---

## verify_contract

Verify the signature of a plugin contract.

```python
verify_contract(self, contract)
```

---

