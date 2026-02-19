# hardware_id API Reference

> **Source**: `src/thegent/security/hardware_id.py`

WP-23002: Hardware-Bound Identity (TPM/SecureEnclave).
Ensures agent identities are bound to physical hardware or secure enclaves.
Provides hardware-attested provenance for agent actions.

---

## HardwareAttestation

Metadata for a hardware-bound identity attestation.

**Inherits from**: `BaseModel`

---

## HardwareIdentityManager

Manages hardware-bound cryptographic identities for agents.

### Methods

#### HardwareIdentityManager.__init__

```python
__init__(self, agent_id)
```

#### HardwareIdentityManager.get_hardware_attestation

Retrieve an attestation token from the local hardware provider.

```python
get_hardware_attestation(self)
```

#### HardwareIdentityManager.verify_attestation

Verify a hardware attestation token.

```python
verify_attestation(self, attestation)
```

---

## get_hardware_attestation

Retrieve an attestation token from the local hardware provider.

```python
get_hardware_attestation(self)
```

---

## verify_attestation

Verify a hardware attestation token.

```python
verify_attestation(self, attestation)
```

---

