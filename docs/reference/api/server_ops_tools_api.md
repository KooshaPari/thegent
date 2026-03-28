# server_ops_tools API Reference

> **Source**: `src/thegent/mcp/server_ops_tools.py`

Ops/provider/audit MCP tool registration helpers.

---

## register_ops_tools

Register selected operation/provider/audit MCP tools.

---

## thegent_list_agents

List available canonical agents for task execution.

---

## thegent_list_models

```python
thegent_list_models(provider: Any, include_contract: bool, by_model: bool)
```

List available AI models and their provider mappings.

---

## thegent_list_modes

```python
thegent_list_modes(mode: Any)
```

List multi-agent orchestration modes (G-KD-04).

---

## thegent_list_operations

```python
thegent_list_operations(operation: Any)
```

List universal operation taxonomy: orchestrate, govern, recover, observe, plan.

---

## thegent_observe_summary

```python
thegent_observe_summary(limit: int, drift_window: int, structural_budget_pct: float, semantic_budget_pct: float, provider: Any, trend_samples: int, top_escalations: int)
```

Get unified observability summary for KPIs, drift budget, and escalations.

---

## thegent_resolve_model_route

```python
thegent_resolve_model_route(model: str, provider: Any, policy: str)
```

Resolve a model to a concrete routing target.

---

## thegent_session_contract_health_gate

```python
thegent_session_contract_health_gate(owner: Any, all: bool, strict: bool, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float)
```

Evaluate session contract health against a minimum ratio gate.

---

## thegent_session_contract_health_report

```python
thegent_session_contract_health_report(owner: Any, all: bool, strict: bool, top_blocked: int, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float)
```

Get contract health report with issue taxonomy and owner-level breakdown.

---

## thegent_session_contract_health_trend

```python
thegent_session_contract_health_trend(payload_type: str, owner: Any, all: bool, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int)
```

Get trend snapshots and deltas for session contract health scopes.

---

## thegent_session_contracts

```python
thegent_session_contracts(owner: Any, all: bool, missing_only: bool, summary_only: bool, strict: bool)
```

List session routing contract metadata and report completeness.

---

## thegent_suggest_mode

```python
thegent_suggest_mode(risk: str, urgency: str, confidence: float)
```

WP-Y1: Suggest multi-agent mode based on risk, urgency, confidence (FR-032).

---

