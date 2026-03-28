# config_defaults API Reference

> **Source**: `src/thegent/config_defaults.py`

Shared defaults and field factories for thegent settings.

---

## autosync_phase1_enabled

Resolve phase-1 autosync enablement behavior.

Phase 1 keeps existing behavior for repos that already opted in while
preserving a hard explicit env override when provided.

---

## default_cost_budget_by_category

Return default per-category monthly cost budget limits.

---

## default_hitl_checkpoints

Return default HITL checkpoints.

---

## default_mac_keep_awake_agents

Return default agents that trigger macOS caffeinate.

---

## default_sandbox_env_allowlist

Return default environment allowlist for sandboxed runs.

---

## default_workstream_autosync_migration_phases

Return the default phased migration plan for autosync enablement.

---

## expanded_path_factory

```python
expanded_path_factory(path: str)
```

Return a zero-arg factory that expands user-relative paths.

---

