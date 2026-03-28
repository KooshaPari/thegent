# governance_policy_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_policy_cmds.py`

Governance policy, contracts, and compliance commands (WL-124).

This module handles policy configuration, contract management, drift detection, and compliance verification.

---

## compliance_plugin_check_cmd

```python
compliance_plugin_check_cmd(plugin_id: str, signature: str)
```

Verify a plugin contract (WP-15003).

---

## compliance_redact_cmd

```python
compliance_redact_cmd(text: str)
```

Test PII/Secret redaction (WP-15005).

---

## compliance_siem_test_cmd

```python
compliance_siem_test_cmd(message: str, severity: str)
```

Test SIEM event egress (WP-15001).

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

## govern_cost_cmd

```python
govern_cost_cmd(owner: Any, days: int, format: Any)
```

Show daily cost aggregation (FR-GOV-002).

---

## guardrails_check_cmd

```python
guardrails_check_cmd(prompt: str, agent: Any, model: Any)
```

Check a prompt against active guardrails (FR-GOV-003..006).

---

## guardrails_show_cmd

Show active guardrail configuration (FR-GOV-007).

---

## migration_cmd

```python
migration_cmd(contract_id: str, version: str, format: Any)
```

Evaluate migration status for a contract version.

---

## policy_check_cmd

```python
policy_check_cmd(agent: str, model: Any, lane: str, confidence: float)
```

Evaluate a hypothetical run against governance policies (WP-3001).

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

## signatures_list_cmd

```python
signatures_list_cmd(limit: int, format: Any)
```

List signed MAIF artifacts (WP-3002).

---

## signatures_verify_cmd

```python
signatures_verify_cmd(run_id: str)
```

Verify a signed MAIF artifact (WP-3002).

---

## trust_status_cmd

```python
trust_status_cmd(format: Any)
```

Show last environment and trust boundary status (WP-3007).

---

