# main API Reference

> **Source**: `src/thegent/cli/apps/main.py`

Thegent 3.0: Unified Agent Orchestration Entry Point.

Consolidates all legacy command sprawl into a clean, logical hierarchy.

---

## agent_server_cmd

---

## domain_map_compat

```python
domain_map_compat(domain_name: str, target: str, mode: str, registrar: str, dns_provider: str, tunnel_name: str, format: str)
```

Compatibility shim for legacy `thegent domain-map` usage.

---

## help_cmd

```python
help_cmd(command: str)
```

Show inline usage examples for COMMAND.

# @trace WL-040 WP-4004

Example::

    thegent help run
    thegent help plan
    thegent help doctor

---

## main_welcome

```python
main_welcome(ctx: typer.Context, _version: bool)
```

---

## session_health_gate_wrapper

```python
session_health_gate_wrapper(all_sessions: bool, owner: Any, strict: bool, format: str, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, output: Any, export_format: Any, overwrite: bool)
```

Evaluate session contract health gate.

---

## session_health_report_wrapper

```python
session_health_report_wrapper(all_sessions: bool, owner: Any, strict: bool, format: str, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, output: Any, export_format: Any, overwrite: bool)
```

Generate session contract health report.

---

## session_health_trend_wrapper

```python
session_health_trend_wrapper(payload_type: str, all_sessions: bool, owner: Any, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, format: str, output: Any, export_format: Any, overwrite: bool)
```

Analyze session contract health trends.

---

