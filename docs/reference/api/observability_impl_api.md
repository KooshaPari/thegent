# observability_impl API Reference

> **Source**: `src/thegent/cli/commands/observability_impl.py`

Thegent observability impl facade - routes to specialized modules.

This module re-exports all observability implementation functions from:
- observability_main_impl: Main impls (observe_summary, sweep, review, compliance)
- observability_health_impl: Health payload and snapshot helpers
- observability_trends_impl: Observe summary trend analysis helpers

Direct imports from submodules preserve all public names for internal usage.

---

