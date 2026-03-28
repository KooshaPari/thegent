# governance_policy_contracts_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_policy_contracts_cmds.py`

Governance policy, contracts, and audit commands (WL-124).

Policy configuration, contract registry, migration, drift detection, and audit.

---

## contracts_conformance_cmd

```python
contracts_conformance_cmd(format: Any, check_drift: bool, drift_window: int)
```

Run provider adapter conformance tests.

---

## contracts_registry_cmd

```python
contracts_registry_cmd(format: Any)
```

Show the contract registry and compatibility matrix.

---

## drift_cmd

```python
drift_cmd(window: int, format: Any, structural_budget: float, semantic_budget: float)
```

Detect significant drift in contract performance and check alert budgets (G-RV-07).

---

## migration_cmd

```python
migration_cmd(contract_id: str, version: str, format: Any)
```

Evaluate migration status for a contract version.

---

## policy_purge_cmd

```python
policy_purge_cmd(dry_run: bool)
```

Purge expired history based on tiered retention (WP-3006).

---

## policy_show_cmd

Show active governance policies and thresholds.

---

## trust_status_cmd

```python
trust_status_cmd(format: Any)
```

Show last environment and trust boundary status (WP-3007).

---

