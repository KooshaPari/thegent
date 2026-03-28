# session_health_report_impl API Reference

> **Source**: `src/thegent/cli/commands/session_health_report_impl.py`

Session contract health report logic.

Extracted from session_health_impl.py as part of WL-120 max-lines enforcement.
Trend logic extracted to session_health_trend_impl.py.
Contains:
- session_contract_health_report_impl: health report with issue taxonomy and owner breakdown

---

## session_contract_health_report_impl

```python
session_contract_health_report_impl(owner: Any, all: bool, strict: bool, top_blocked: int, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float)
```

Return health report with issue taxonomy and owner-level breakdown.

---

