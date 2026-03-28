# session_impl API Reference

> **Source**: `src/thegent/cli/commands/session_impl.py`

Session management backend: thin re-export facade.

Extracted from impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2).
Split into sub-modules as part of WL-120 max-lines enforcement:
- session_meta_impl.py        — meta I/O, state contracts, output helpers, continuation
- session_health_impl.py      — contract listing, audit, health gate
- session_health_report_impl.py — health report with issue taxonomy
- session_health_trend_impl.py  — health trend snapshots and deltas
- session_ops_impl.py         — ps, list, status, inspect, logs
- session_control_impl.py     — wait, stop, send, history, metrics, prune, events,
                                meta, negotiate, purge, explain

---

