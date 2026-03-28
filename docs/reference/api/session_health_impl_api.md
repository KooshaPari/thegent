# session_health_impl API Reference

> **Source**: `src/thegent/cli/commands/session_health_impl.py`

Session contract listing, audit, and health gate logic.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
health_report_impl and health_trend_impl split to session_health_report_impl.py.
Contains:
- _extract_blocked_ratio: helper for blocked ratio extraction
- list_session_contracts_impl: list sessions with contract metadata and quality signal
- session_contract_audit_impl: session contract audit rows with filtering and summary
- session_contract_health_gate_impl: evaluate routing contract health against a minimum ratio gate

---

## list_session_contracts_impl

```python
list_session_contracts_impl(owner: Any, all: bool, strict: bool)
```

Return sessions with route-request/route-contract metadata and contract quality signal.

---

## session_contract_audit_impl

```python
session_contract_audit_impl(owner: Any, all: bool, missing_only: bool, summary_only: bool, strict: bool)
```

Return session contract audit rows with optional filtering and summary.

---

## session_contract_health_gate_impl

```python
session_contract_health_gate_impl(owner: Any, all: bool, strict: bool, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float)
```

Evaluate routing contract health against a minimum healthy-ratio gate.

---

