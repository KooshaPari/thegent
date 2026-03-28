# compliance API Reference

> **Source**: `src/thegent/governance/compliance.py`

WP-15004: Certification export profiles for SOC 2, ISO, and EU AI Act.

---

## AuditExporter

Export compliance evidence as structured JSON for regulators (WL-051).

### Methods

#### AuditExporter.__init__

```python
__init__(self: Any, evidence_store: EvidenceStore)
```

---

#### AuditExporter.enforce_integrity

```python
enforce_integrity(self: Any)
```

Fail loudly when evidence chain integrity cannot be verified.

---

#### AuditExporter.export_checkpoint

```python
export_checkpoint(self: Any)
```

Export a deterministic checkpoint summary with evidence digest.

---

#### AuditExporter.export_json

```python
export_json(self: Any)
```

Export evidence to a structured JSON document.

**Parameters**:

- `output_path`: If provided, write JSON to this path.
- `since_days`: If provided, only include records from the last N days.
- `kind_filter`: If provided, only include records of these kinds.

---

#### AuditExporter.reconcile_export

```python
reconcile_export(self: Any)
```

Validate exported record count against an expected value.

---

---

## ComplianceAuditTrail

Maintains audit trail for compliance verification.

### Methods

#### ComplianceAuditTrail.__init__

```python
__init__(self: Any, storage_path: Path)
```

---

#### ComplianceAuditTrail.record_action

```python
record_action(self: Any, action: str, context: dict[(str, Any)], profile: ComplianceProfile)
```

Record an action in the audit trail.

---

---

## ComplianceControl

Represents a compliance control requirement.

---

## ComplianceEnforcer

Enforces compliance controls based on active profile.

### Methods

#### ComplianceEnforcer.__init__

```python
__init__(self: Any, profile: ComplianceProfile)
```

---

#### ComplianceEnforcer.check_control

```python
check_control(self: Any, control_id: str, context: dict[(str, Any)])
```

Check if a control is satisfied.

---

#### ComplianceEnforcer.enforce_mandatory

```python
enforce_mandatory(self: Any, action: str, context: dict[(str, Any)])
```

Enforce all mandatory controls for an action.

---

---

## ComplianceEvidence

Single tamper-evident compliance evidence record (WL-051).

**Inherits from**: `_BaseModel`

### Methods

#### ComplianceEvidence.compute_hash

```python
compute_hash(entry: dict, prev_hash: str)
```

Compute SHA-256 hash over canonical JSON + prev_hash.

---

---

## ComplianceExporter

Exports framework-specific evidence bundles for compliance audits (WP-15004).

### Methods

#### ComplianceExporter.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### ComplianceExporter.export_bundle

```python
export_bundle(self: Any, framework: str, target_path: Path)
```

Generate an evidence bundle for a specific compliance framework.

---

---

## ComplianceProfile

Represents a compliance profile with controls.

### Methods

#### ComplianceProfile.get_mandatory_controls

```python
get_mandatory_controls(self: Any)
```

Get all mandatory controls.

---

---

## ComplianceProfileType

**Inherits from**: `Enum`

---

## ConsentRecord

Tracks consent granted by a data subject (GDPR Art. 7, WL-051).

**Inherits from**: `_BaseModel`

---

## EvidenceStore

Append-only JSONL evidence store with hash-chain integrity (SOC-2, WL-051).

Each record's entry_hash covers the record content + the previous record's
entry_hash, forming a tamper-evident chain.  verify_integrity() walks the
full chain and raises ValueError on any mismatch.

### Methods

#### EvidenceStore.__init__

```python
__init__(self: Any, store_path: Path)
```

---

#### EvidenceStore.append

```python
append(self: Any)
```

Append a new evidence record and return it.

---

#### EvidenceStore.list_all

```python
list_all(self: Any)
```

Return all evidence records in append order.

---

#### EvidenceStore.list_since

```python
list_since(self: Any, cutoff_utc: datetime)
```

Return evidence records created at or after cutoff_utc.

---

#### EvidenceStore.purge_older_than

```python
purge_older_than(self: Any, days: int)
```

Remove records older than `days` days. Returns count purged.

The surviving records are rewritten with a rebuilt hash chain so
integrity checks still pass after purge.

---

#### EvidenceStore.verify_integrity

```python
verify_integrity(self: Any)
```

Walk the hash chain and return True if all hashes are consistent.

---

---

## RetentionEnforcer

Enforces GDPR retention policies with consent tracking (WL-051).

Data store layout (base_dir):
    policies.jsonl   — retention policy records
    consent.jsonl    — consent records
    purge_log.jsonl  — purge execution audit trail

### Methods

#### RetentionEnforcer.__init__

```python
__init__(self: Any, base_dir: Path)
```

---

#### RetentionEnforcer.add_policy

```python
add_policy(self: Any, policy: RetentionPolicy)
```

Register a retention policy (idempotent on policy_id).

---

#### RetentionEnforcer.get_policy

```python
get_policy(self: Any, policy_id: str)
```

---

#### RetentionEnforcer.has_active_consent

```python
has_active_consent(self: Any)
```

Return True if a non-withdrawn consent exists for the subject+category.

---

#### RetentionEnforcer.list_consents

```python
list_consents(self: Any, tenant_id: Any)
```

---

#### RetentionEnforcer.list_policies

```python
list_policies(self: Any)
```

---

#### RetentionEnforcer.purge_tenant_data

```python
purge_tenant_data(self: Any)
```

Apply all retention policies for a tenant and purge expired evidence.

Raises RuntimeError if consent is required but missing.
Returns a summary dict with purge counts per policy.

---

#### RetentionEnforcer.record_consent

```python
record_consent(self: Any, record: ConsentRecord)
```

Append a consent record.

---

---

## RetentionPolicy

Policy definition for GDPR data retention (WL-051).

**Inherits from**: `_BaseModel`

---

## add_policy

```python
add_policy(self: Any, policy: RetentionPolicy)
```

Register a retention policy (idempotent on policy_id).

---

## append

```python
append(self: Any)
```

Append a new evidence record and return it.

---

## check_control

```python
check_control(self: Any, control_id: str, context: dict[(str, Any)])
```

Check if a control is satisfied.

---

## compute_hash

```python
compute_hash(entry: dict, prev_hash: str)
```

Compute SHA-256 hash over canonical JSON + prev_hash.

---

## enforce_integrity

```python
enforce_integrity(self: Any)
```

Fail loudly when evidence chain integrity cannot be verified.

---

## enforce_mandatory

```python
enforce_mandatory(self: Any, action: str, context: dict[(str, Any)])
```

Enforce all mandatory controls for an action.

---

## export_bundle

```python
export_bundle(self: Any, framework: str, target_path: Path)
```

Generate an evidence bundle for a specific compliance framework.

---

## export_checkpoint

```python
export_checkpoint(self: Any)
```

Export a deterministic checkpoint summary with evidence digest.

---

## export_json

```python
export_json(self: Any)
```

Export evidence to a structured JSON document.

**Parameters**:

- `output_path`: If provided, write JSON to this path.
- `since_days`: If provided, only include records from the last N days.
- `kind_filter`: If provided, only include records of these kinds.

---

## get_mandatory_controls

```python
get_mandatory_controls(self: Any)
```

Get all mandatory controls.

---

## get_policy

```python
get_policy(self: Any, policy_id: str) -> RetentionPolicy
```

---

## has_active_consent

```python
has_active_consent(self: Any)
```

Return True if a non-withdrawn consent exists for the subject+category.

---

## list_all

```python
list_all(self: Any)
```

Return all evidence records in append order.

---

## list_consents

```python
list_consents(self: Any, tenant_id: Any) -> list
```

---

## list_policies

```python
list_policies(self: Any) -> list
```

---

## list_since

```python
list_since(self: Any, cutoff_utc: datetime)
```

Return evidence records created at or after cutoff_utc.

---

## purge_older_than

```python
purge_older_than(self: Any, days: int)
```

Remove records older than `days` days. Returns count purged.

The surviving records are rewritten with a rebuilt hash chain so
integrity checks still pass after purge.

---

## purge_tenant_data

```python
purge_tenant_data(self: Any)
```

Apply all retention policies for a tenant and purge expired evidence.

Raises RuntimeError if consent is required but missing.
Returns a summary dict with purge counts per policy.

---

## reconcile_export

```python
reconcile_export(self: Any)
```

Validate exported record count against an expected value.

---

## record_action

```python
record_action(self: Any, action: str, context: dict[(str, Any)], profile: ComplianceProfile)
```

Record an action in the audit trail.

---

## record_consent

```python
record_consent(self: Any, record: ConsentRecord)
```

Append a consent record.

---

## verify_integrity

```python
verify_integrity(self: Any)
```

Walk the hash chain and return True if all hashes are consistent.

---

