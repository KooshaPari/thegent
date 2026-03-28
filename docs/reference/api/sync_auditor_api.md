# sync_auditor API Reference

> **Source**: `src/thegent/integrations/sync_auditor.py`

Sync policy auditor for runtime validation.

# @trace WL-261

---

## LocalOrphanReport

Structured report of local items without remote tracker mapping.

**Inherits from**: `SerializableMixin`

---

## RemoteOrphanReport

Structured report of remote items not represented locally.

**Inherits from**: `SerializableMixin`

---

## SyncAuditor

Auditor for sync policies.

### Methods

#### SyncAuditor.__init__

```python
__init__(self: Any)
```

Initialize the sync auditor.

---

#### SyncAuditor.append_artifact

```python
append_artifact(self: Any)
```

Append a signed artifact to the in-memory audit chain.

---

#### SyncAuditor.artifact_chain

```python
artifact_chain(self: Any)
```

Return audit chain artifacts as dictionaries.

---

#### SyncAuditor.audit

```python
audit(self: Any)
```

Run the sync policy audit.

**Returns**: SyncPolicyAudit with current policies.

---

#### SyncAuditor.audit_as_dict

```python
audit_as_dict(self: Any)
```

Get audit result as dictionary.

**Returns**: Dictionary representation of audit result.

---

#### SyncAuditor.audit_as_json

```python
audit_as_json(self: Any)
```

Get audit result as JSON string.

**Returns**: JSON representation of audit result.

---

#### SyncAuditor.detect_local_orphans

```python
detect_local_orphans(local_ids: list[str], mapped_remote_ids: list[str])
```

Return local IDs that are not present in remote tracker mappings.

---

#### SyncAuditor.detect_remote_orphans

```python
detect_remote_orphans(remote_ids: list[str], local_ids: list[str])
```

Return remote IDs that are missing from local WORK_STREAM IDs.

---

#### SyncAuditor.generate_html_diff_artifact

```python
generate_html_diff_artifact(local_snapshot: dict[(str, Any)], remote_snapshot: dict[(str, Any)], out_path: Path)
```

Generate deterministic side-by-side HTML diff artifact.

---

#### SyncAuditor.load_policy_contract

```python
load_policy_contract(self: Any)
```

Load `.thegent/sync-policy.yaml` and map it into audit surfaces.

---

#### SyncAuditor.set_enabled_connectors

```python
set_enabled_connectors(self: Any, connectors: list[str])
```

Set the list of enabled connectors.

**Parameters**:

- `connectors`: List of enabled connector names.

---

#### SyncAuditor.set_policy_modes

```python
set_policy_modes(self: Any, modes: dict[(str, str)])
```

Set policy enforcement modes for connectors.

**Parameters**:

- `modes`: Dictionary mapping connector names to policy modes
(e.g., 'enforce', 'warn', 'disabled').

---

#### SyncAuditor.set_quota_budgets

```python
set_quota_budgets(self: Any, budgets: dict[(str, int)])
```

Set quota budgets for connectors.

**Parameters**:

- `budgets`: Dictionary mapping connector names to daily quota limits.

---

#### SyncAuditor.validate_policy

```python
validate_policy(self: Any)
```

Validate sync policy configuration.

**Returns**: Tuple of (is_valid, list_of_issues).

---

#### SyncAuditor.verify_artifact_chain

```python
verify_artifact_chain(self: Any, secret: str)
```

Verify that the artifact chain is continuous and signatures are valid.

---

---

## SyncPolicyAudit

Sync policy audit result.

---

## append_artifact

```python
append_artifact(self: Any)
```

Append a signed artifact to the in-memory audit chain.

---

## artifact_chain

```python
artifact_chain(self: Any)
```

Return audit chain artifacts as dictionaries.

---

## audit

```python
audit(self: Any)
```

Run the sync policy audit.

**Returns**: SyncPolicyAudit with current policies.

---

## audit_as_dict

```python
audit_as_dict(self: Any)
```

Get audit result as dictionary.

**Returns**: Dictionary representation of audit result.

---

## audit_as_json

```python
audit_as_json(self: Any)
```

Get audit result as JSON string.

**Returns**: JSON representation of audit result.

---

## detect_local_orphans

```python
detect_local_orphans(local_ids: list[str], mapped_remote_ids: list[str])
```

Return local IDs that are not present in remote tracker mappings.

---

## detect_remote_orphans

```python
detect_remote_orphans(remote_ids: list[str], local_ids: list[str])
```

Return remote IDs that are missing from local WORK_STREAM IDs.

---

## generate_html_diff_artifact

```python
generate_html_diff_artifact(local_snapshot: dict[(str, Any)], remote_snapshot: dict[(str, Any)], out_path: Path)
```

Generate deterministic side-by-side HTML diff artifact.

---

## load_policy_contract

```python
load_policy_contract(self: Any)
```

Load `.thegent/sync-policy.yaml` and map it into audit surfaces.

---

## set_enabled_connectors

```python
set_enabled_connectors(self: Any, connectors: list[str])
```

Set the list of enabled connectors.

**Parameters**:

- `connectors`: List of enabled connector names.

---

## set_policy_modes

```python
set_policy_modes(self: Any, modes: dict[(str, str)])
```

Set policy enforcement modes for connectors.

**Parameters**:

- `modes`: Dictionary mapping connector names to policy modes
(e.g., 'enforce', 'warn', 'disabled').

---

## set_quota_budgets

```python
set_quota_budgets(self: Any, budgets: dict[(str, int)])
```

Set quota budgets for connectors.

**Parameters**:

- `budgets`: Dictionary mapping connector names to daily quota limits.

---

## validate_policy

```python
validate_policy(self: Any)
```

Validate sync policy configuration.

**Returns**: Tuple of (is_valid, list_of_issues).

---

## verify_artifact_chain

```python
verify_artifact_chain(self: Any, secret: str)
```

Verify that the artifact chain is continuous and signatures are valid.

---

