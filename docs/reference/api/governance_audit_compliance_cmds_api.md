# governance_audit_compliance_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_audit_compliance_cmds.py`

Governance audit, signatures, and compliance commands (WL-124).

Signed artifacts, audit, SIEM, plugin verification, and guardrails.

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

