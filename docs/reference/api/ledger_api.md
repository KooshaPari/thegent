# ledger API Reference

> **Source**: `src/thegent/governance/ledger.py`

WP-5006: Ledger integrity verification.

---

## IncidentLedger

Immutable incident ledger with rolling hash chain (WP-15002).

**Inherits from**: `LedgerVerifier`

### Methods

#### IncidentLedger.__init__

```python
__init__(self, ledger_path)
```

#### IncidentLedger.get_run_artifacts

Return all artifacts for run_id.

```python
get_run_artifacts(self, run_id)
```

#### IncidentLedger.record_artifact

Append artifact with rolling hash; return computed hash.

```python
record_artifact(self, run_id, action, payload)
```

#### IncidentLedger.verify_integrity

```python
verify_integrity(self)
```

---

## LedgerVerifier

Verifies the integrity of the action ledger using rolling hashes.

### Methods

#### LedgerVerifier.__init__

```python
__init__(self, ledger_path)
```

#### LedgerVerifier.verify_integrity

Verify the rolling hash chain in the ledger.

```python
verify_integrity(self)
```

---

## get_run_artifacts

Return all artifacts for run_id.

```python
get_run_artifacts(self, run_id)
```

---

## record_artifact

Append artifact with rolling hash; return computed hash.

```python
record_artifact(self, run_id, action, payload)
```

---

## verify_integrity

```python
verify_integrity(self)
```

---

