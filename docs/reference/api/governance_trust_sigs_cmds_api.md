# governance_trust_sigs_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_trust_sigs_cmds.py`

Governance policy, contracts, and compliance commands (WL-124).

This module handles policy configuration, contract management, drift detection, and compliance verification.

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

