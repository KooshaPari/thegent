# infra_observe_cmds API Reference

> **Source**: `src/thegent/cli/commands/infra_observe_cmds.py`

Thegent CLI observability commands (observe, cockpit, sitback) - extracted from infra_cmds.py.

---

## cockpit_cmd

Show high-level operator cockpit summary.

---

## observe_summary_cmd

```python
observe_summary_cmd(limit: int, drift_window: int, structural_budget: float, semantic_budget: float, format: Any, provider: Any, trend_samples: int, top_escalations: int)
```

FR-X08: Unified observability summary (KPIs, drift, escalation).

---

## sitback_dashboard_cmd

```python
sitback_dashboard_cmd(refresh: Any, format: Any, profile: str)
```

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.

---

