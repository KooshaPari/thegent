# Cost-Based Routing — Deferred Scope

**Date:** 2026-02-14  
**Status:** Documented as deferred (R8, Optional→Required)  
**Source:** `docs/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md`, gaps doc R8

---

## 1. What Exists Today

- **`cost_weight` on Route** (`src/thegent/models/catalog.py`): Each route has a static `cost_weight` (lower = cheaper). Static catalog assigns weights per provider/model (e.g. gemini-3-flash 0.1, claude-opus 1.0).
- **`cheapest` routing policy**: When policy is `cheapest`, routes are sorted by `cost_weight` then priority. Implemented in `resolve_route()`.
- **Scraped routes**: Use defaults (proxy 0.8, direct 0.3) when no static weight exists.

---

## 2. Deferred / Out of Scope

The following are **not implemented** and are documented as deferred:

| Item | Description | Reference |
|------|-------------|-----------|
| Per-run cost tracking | Aggregate actual cost per run; budget alerts | FR-036, WP-Y4 |
| Cost-per-quality optimization | RouteLLM-style provider selection; A/B cost-quality trade-off | WP-5003, NFR-016 |
| Dynamic cost weights | Cost weights from live pricing or usage data | — |
| Budget enforcement | Hard limits per run or per hour; throttle on overage | Risk registry TD-02 |

---

## 3. Future Work

When cost-based routing is prioritized:

1. Implement `orchestration/cost.py` (WP-Y4) for per-run cost aggregation.
2. Add budget alerts and cost-overage gates.
3. Integrate cost tracking with run registry for historical analysis.
4. Consider RouteLLM or similar for cost-quality optimization (WP-5003).

---

## 4. References

- `docs/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md` §3.1, §3.2
- `docs/unified-plan/04-REQUIREMENTS.md` FR-036, NFR-016
- `docs/unified-plan/02-UNIFIED-WBS.md` WP-Y4, WP-5003
- `docs/docset/RISKS_AND_ANTIPATTERNS.md` (cost optimization risks)
