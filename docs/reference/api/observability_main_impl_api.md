# observability_main_impl API Reference

> **Source**: `src/thegent/cli/commands/observability_main_impl.py`

Observability implementation facade (WL-120).

Re-exports split modules:
- observability_escalation_impl: escalation, sweep
- observability_governance_impl: governance, review, compliance
- observability_trends_impl: summary (lazy import)

---

## observe_summary_impl

```python
observe_summary_impl(limit: int, drift_window: int, structural_budget_pct: float, semantic_budget_pct: float, provider: Any, top_escalations: int, trend_samples: int)
```

FR-X08: Unified observability summary (lazy import from trends impl).

---

