# server_contract_wrappers API Reference

> **Source**: `src/thegent/mcp/server_contract_wrappers.py`

Wrapper functions for contract health checks in thegent MCP server.

---

## resource_session_contract_health_trend

```python
resource_session_contract_health_trend(payload_type: str, owner: Any, all: bool, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, resource_impl: Any, session_contract_health_trend_impl_fn: Any, stable_json: Any)
```

Wrapper for resource session contract health trend.

---

## thegent_observe_summary

```python
thegent_observe_summary(limit: int, drift_window: int, structural_budget_pct: float, semantic_budget_pct: float, provider: Any, trend_samples: int, top_escalations: int, server_tools_contract_observe: Any, observe_summary_impl_fn: Any, stable_json: Any)
```

Wrapper for thegent observe summary.

---

## thegent_session_contract_health_gate

```python
thegent_session_contract_health_gate(owner: Any, all: bool, strict: bool, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, session_contract_health_gate_impl_fn: Any, stable_json: Any)
```

Wrapper for thegent session contract health gate.

---

## thegent_session_contract_health_report

```python
thegent_session_contract_health_report(owner: Any, all: bool, strict: bool, top_blocked: int, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, session_contract_health_report_impl_fn: Any, stable_json: Any)
```

Wrapper for thegent session contract health report.

---

## thegent_session_contract_health_trend

```python
thegent_session_contract_health_trend(payload_type: str, owner: Any, all: bool, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, server_tools_contract_observe: Any, session_contract_health_trend_impl_fn: Any, stable_json: Any, coerce_issue_types_fn: Any)
```

Wrapper for thegent session contract health trend.

---

