# policy_checksum API Reference

> **Source**: `src/thegent/integrations/policy_checksum.py`

Policy data integrity verification via checksumming.

Computes and tracks checksums of policy data to detect unintended drift
and changes during runtime.

FR traceability: WL-312 (Policy Checksum Drift Detection)

---

## PolicyChecksum

Record of a policy checksum baseline.

---

## PolicyChecksumDriftDetector

Detects policy data drift via checksum comparisons.

### Methods

#### PolicyChecksumDriftDetector.__init__

```python
__init__(self: Any)
```

Initialize the detector with empty baseline store.

---

#### PolicyChecksumDriftDetector.check_drift

```python
check_drift(self: Any, policy_id: str, current_data: dict)
```

Check if current policy data has drifted from baseline.

**Parameters**:

- `policy_id`: Identifier for the policy.
- `current_data`: Current policy data dictionary.

**Returns**: True if checksum differs from baseline (drift detected),
False if checksums match (no drift).

---

#### PolicyChecksumDriftDetector.compute_checksum

```python
compute_checksum(self: Any, policy_data: dict)
```

Compute SHA256 checksum of policy data.

**Parameters**:

- `policy_data`: Policy data dictionary.

**Returns**: SHA256 hex digest of the sorted JSON serialization.

---

#### PolicyChecksumDriftDetector.get_baseline

```python
get_baseline(self: Any, policy_id: str)
```

Retrieve the baseline for a policy.

**Parameters**:

- `policy_id`: Identifier for the policy.

**Returns**: The PolicyChecksum baseline.

---

#### PolicyChecksumDriftDetector.record_baseline

```python
record_baseline(self: Any, policy_id: str, policy_data: dict, cycle_id: str)
```

Record a baseline checksum for a policy.

**Parameters**:

- `policy_id`: Identifier for the policy.
- `policy_data`: Policy data dictionary.
- `cycle_id`: Associated cycle identifier.

**Returns**: The PolicyChecksum baseline that was recorded.

---

---

## check_drift

```python
check_drift(self: Any, policy_id: str, current_data: dict)
```

Check if current policy data has drifted from baseline.

**Parameters**:

- `policy_id`: Identifier for the policy.
- `current_data`: Current policy data dictionary.

**Returns**: True if checksum differs from baseline (drift detected),
False if checksums match (no drift).

**Raises**:

- `KeyError`: If no baseline exists for the policy_id.

---

## compute_checksum

```python
compute_checksum(self: Any, policy_data: dict)
```

Compute SHA256 checksum of policy data.

**Parameters**:

- `policy_data`: Policy data dictionary.

**Returns**: SHA256 hex digest of the sorted JSON serialization.

---

## compute_payload_checksum

```python
compute_payload_checksum(payload: Any)
```

Compute a deterministic SHA256 checksum for a JSON-compatible payload.

---

## get_baseline

```python
get_baseline(self: Any, policy_id: str)
```

Retrieve the baseline for a policy.

**Parameters**:

- `policy_id`: Identifier for the policy.

**Returns**: The PolicyChecksum baseline.

**Raises**:

- `KeyError`: If no baseline exists for the policy_id.

---

## record_baseline

```python
record_baseline(self: Any, policy_id: str, policy_data: dict, cycle_id: str)
```

Record a baseline checksum for a policy.

**Parameters**:

- `policy_id`: Identifier for the policy.
- `policy_data`: Policy data dictionary.
- `cycle_id`: Associated cycle identifier.

**Returns**: The PolicyChecksum baseline that was recorded.

---

## verify_payload_checksum

```python
verify_payload_checksum(payload: Any, expected_checksum: str)
```

Validate payload checksum and fail loudly on mismatch.

---

