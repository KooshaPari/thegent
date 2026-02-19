# tee_check API Reference

> **Source**: `src/thegent/governance/tee_check.py`

WP-23003: Attestable Execution Environments (TEE) check.

Provides verification logic for secure enclave execution.

---

## TEEAttestation

TEE Attestation report (WP-23003).

---

## TEEChecker

Verifies if the agent is running in a trusted execution environment.

### Methods

#### TEEChecker.__init__

```python
__init__(self, mock_mode)
```

#### TEEChecker.check

Perform TEE check and return attestation.

```python
check(self)
```

#### TEEChecker.enforce_tee

Raise error if not running in TEE and environment requires it.

```python
enforce_tee(self)
```

---

## TEEType

**Inherits from**: `Enum`

---

## check

Perform TEE check and return attestation.

```python
check(self)
```

---

## enforce_tee

Raise error if not running in TEE and environment requires it.

```python
enforce_tee(self)
```

---

## get_tee_attestation

Helper for governance audit emission.

---

