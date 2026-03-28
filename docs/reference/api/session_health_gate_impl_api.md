# session_health_gate_impl API Reference

> **Source**: `src/thegent/cli/commands/session_health_gate_impl.py`

Session contract health gate evaluation logic.

Extracted from session_health_impl.py as part of WL-120 LOC Reduction Program.
Contains:
- session_contract_health_gate_impl: evaluate routing contract health against a minimum ratio gate
- Policy resolution, baseline comparison, trend tracking

---

## session_contract_health_gate_impl

```python
session_contract_health_gate_impl(owner: Any, all: bool, strict: bool, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float)
```

Evaluate routing contract health against a minimum healthy-ratio gate.

---

