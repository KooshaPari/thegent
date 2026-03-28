# drift_severity API Reference

> **Source**: `src/thegent/integrations/drift_severity.py`

Status drift severity classification for sync operations.

Classifies status drift into severity tiers and defines escalation thresholds
based on age and status changes.

FR traceability: WL-181 (Status Drift Severity Classification)

---

## DriftEscalationThresholds

Configurable escalation thresholds for drift severity.

### Methods

#### DriftEscalationThresholds.validate

```python
validate(self: Any)
```

Validate threshold ordering.

**Returns**: True if thresholds are in ascending order.

---

---

## DriftSeverity

Severity tiers for status drift.

**Inherits from**: `str, Enum`

---

## classify_drift

```python
classify_drift(local_status: str, remote_status: str, age_hours: float, thresholds: Any)
```

Classify status drift by age and severity.

Classification logic:
- If status differs, escalate by age: age > critical → CRITICAL,
  age > high → HIGH, age > medium → MEDIUM, else LOW.
- If status matches, return LOW (no drift).

**Parameters**:

- `local_status`: The local status value.
- `remote_status`: The remote status value.
- `age_hours`: Time elapsed since drift occurred (in hours).
- `thresholds`: Escalation thresholds. Uses defaults if None.

**Returns**: The severity classification.

**Raises**:

- `ValueError`: If age_hours is negative.

---

## get_default_thresholds

Get default escalation thresholds.

**Returns**: Default thresholds: 6h (MEDIUM), 24h (HIGH), 72h (CRITICAL).

---

## validate

```python
validate(self: Any)
```

Validate threshold ordering.

**Returns**: True if thresholds are in ascending order.

**Raises**:

- `ValueError`: If thresholds are not in ascending order.

---

