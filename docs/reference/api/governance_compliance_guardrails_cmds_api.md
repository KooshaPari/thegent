# governance_compliance_guardrails_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_compliance_guardrails_cmds.py`

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

## policy_check_cmd

```python
policy_check_cmd(agent: str, model: Any, lane: str, confidence: float)
```

Evaluate a hypothetical run against governance policies (WP-3001).

---

