# sync_policy_contract API Reference

> **Source**: `src/thegent/integrations/sync_policy_contract.py`

Sync policy file contract.

Defines and validates sync policy contracts that govern connector behavior
during synchronization operations.

# @trace WL-197

---

## ConnectorPolicy

Connector-specific sync policy controls.

---

## SimplePolicy

Simple policy contract for WL-197 (backward compat wrapper).

**Inherits from**: `SyncPolicyContract`

**Method Resolution Order**: `SimplePolicy -> SyncPolicyContract`

### Methods

#### SimplePolicy.__init__

```python
__init__(self: Any, version: str, allowed_connectors: list[str], max_batch_size: int, dry_run: bool)
```

Initialize simple policy.

---

---

## SyncPolicyContract

Structured sync policy contract.

Can be instantiated in two ways:
1. Full mode with schema_version, connectors, tenancy (from YAML file)
2. Simple mode with version, allowed_connectors, max_batch_size, dry_run (WL-197)

---

## SyncPolicyValidator

Validates sync policy contracts against defined rules (WL-197).

### Methods

#### SyncPolicyValidator.validate

```python
validate(self: Any, policy: SyncPolicyContract)
```

Validate a sync policy contract.

Checks:
- version is non-empty
- allowed_connectors is non-empty
- max_batch_size > 0

**Parameters**:

- `policy`: The SyncPolicyContract to validate.

**Returns**: List of validation error messages. Empty list means validation passed.

---

---

## TenantConfig

Top-level tenancy configuration.

---

## TenantProject

Tenant-aware project mapping.

---

## load_sync_policy_contract

Load and validate a sync-policy contract.

---

## resolve_sync_policy_path

Resolve the policy path from env override or project root.

---

## validate

```python
validate(self: Any, policy: SyncPolicyContract)
```

Validate a sync policy contract.

Checks:
- version is non-empty
- allowed_connectors is non-empty
- max_batch_size > 0

**Parameters**:

- `policy`: The SyncPolicyContract to validate.

**Returns**: List of validation error messages. Empty list means validation passed.

---

