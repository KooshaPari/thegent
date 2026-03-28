# session_contract_cmds API Reference

> **Source**: `src/thegent/cli/commands/session_contract_cmds.py`

Thegent CLI session commands domain - extracted from cli.py (WL-124).

---

## session_contract_health_gate_cmd

```python
session_contract_health_gate_cmd(all_sessions: bool, owner: Any, strict: bool, format: Any, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contract_health_report_cmd

```python
session_contract_health_report_cmd(all_sessions: bool, owner: Any, strict: bool, top_blocked: int, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, format: Any, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contract_health_trend_cmd

```python
session_contract_health_trend_cmd(payload_type: str, all_sessions: bool, owner: Any, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, format: Any, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contracts_cmd

```python
session_contracts_cmd(all_sessions: bool, owner: Any, format: Any, missing_only: bool, summary_only: bool, strict: bool) -> None
```

---

