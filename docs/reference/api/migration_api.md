# migration API Reference

> **Source**: `src/thegent/contracts/migration.py`

Contract Migration Controller.

Manages the transition between contract versions, enforces deprecation policies,
and evaluates migration window compliance.

---

## MigrationController

Controls and monitors contract version migrations (WP-7008).

### Methods

#### MigrationController.__init__

```python
__init__(self, registry)
```

#### MigrationController.evaluate_version

Evaluate if a contract version is suitable for current use.

Returns:
    Dictionary with keys: 'allowed', 'status', 'reason', 'migration_days_left'.

```python
evaluate_version(self, contract_id, version)
```

#### MigrationController.get_preferred_version

Return the latest non-deprecated version for a contract ID.

```python
get_preferred_version(self, contract_id)
```

#### MigrationController.set_canary

Set canary rollout percentage (WP-7008).

```python
set_canary(self, percentage)
```

#### MigrationController.set_dual_write

Enable or disable dual-write mode (WP-7008).

```python
set_dual_write(self, enabled)
```

#### MigrationController.should_use_new_version

Determine if a run should use the target migration version based on canary.

```python
should_use_new_version(self, run_id)
```

---

## evaluate_version

Evaluate if a contract version is suitable for current use.

Returns:
    Dictionary with keys: 'allowed', 'status', 'reason', 'migration_days_left'.

```python
evaluate_version(self, contract_id, version)
```

---

## get_preferred_version

Return the latest non-deprecated version for a contract ID.

```python
get_preferred_version(self, contract_id)
```

---

## set_canary

Set canary rollout percentage (WP-7008).

```python
set_canary(self, percentage)
```

---

## set_dual_write

Enable or disable dual-write mode (WP-7008).

```python
set_dual_write(self, enabled)
```

---

## should_use_new_version

Determine if a run should use the target migration version based on canary.

```python
should_use_new_version(self, run_id)
```

---

