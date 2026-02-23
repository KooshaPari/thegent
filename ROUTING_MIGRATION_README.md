# Routing Module → CLIProxy Migration

## Status: Phase 1-2 Complete ✅

Infrastructure layer complete. 8 files created. Ready for implementation phase.

## What Was Created

### 1. New HTTP Router Wrapper
```
src/thegent/cliproxy_router.py (production-ready)
```
Provides async HTTP client for CLIProxy `/v1/routing/select` endpoint.

**Key classes:**
- `CLIProxyRouter` — async client
- `RoutingSelection` — response dataclass
- `RoutingConstraints` — request dataclass

**Usage:**
```python
router = CLIProxyRouter()
selection = await router.select_model(RoutingConstraints(
    task_complexity="medium",
    max_cost_per_call=1.0
))
model_id = selection.model_id
```

### 2. Compatibility Shims (re-exports, minimal)
```
src/thegent/utils/model_registry.py          (4 LOC)
src/thegent/utils/model_mapping.py           (6 LOC)
src/thegent/utils/grounding.py               (9 LOC)
src/thegent/utils/provider_types.py          (7 LOC)
src/thegent/utils/ollama_provider.py         (7 LOC)
```

Each re-exports from `thegent.routing.*` to allow simple import migrations:
```python
# Before:
from thegent.routing.grounding import extract_grounding_sources

# After:
from thegent.utils.grounding import extract_grounding_sources
# Rest of code unchanged!
```

### 3. Documentation (1000+ lines)

**Main Plan:** `docs/research/ROUTING_MODULE_CLIPPROXY_MIGRATION_PLAN.md`
- Executive summary
- Architecture overview
- CLIProxy API details
- Phase-by-phase breakdown
- Success criteria
- Timeline & effort

**Implementation Checklist:** `docs/research/ROUTING_MIGRATION_CHECKLIST.md`
- File-by-file instructions (22 files)
- Code examples & patterns
- Status tracking (☐ TODO)
- Tips for implementation

**Status:** `docs/research/ROUTING_MIGRATION_STATUS.md`
- Current progress
- What's done vs. remaining
- Next steps

## Callers to Migrate (22 files, 72 imports)

### Simple Import Replacements (8 files, 1-2 hours)
```
src/thegent/cli/commands/run_output_helpers.py (1 line)
src/thegent/cli/services/run_input_helpers.py (1 line)
src/thegent/cli/services/run_model_helpers.py (2 lines)
src/thegent/cliproxy_models_transform.py (1 line)
src/thegent/cliproxy_request_transform.py (1 line)
src/thegent/cost/aggregator.py (1 line)
src/thegent/models/catalog.py (1 line)
src/thegent/cliproxy_adapter.py (2-3 lines)
```

### Complex Routing Logic (12 files, 3-6 hours)
```
src/thegent/cli/commands/impl.py
src/thegent/cli/tui/pareto.py
src/thegent/models/catalog.py
src/thegent/planning/auto_launch.py
src/thegent/cli/commands/run_cmds.py
src/thegent/mcp/server/tools_terminal.py
src/thegent/orchestration/execution/engine.py
src/thegent/cli/services/run_execution_core_helpers.py
src/thegent/commands/router.py
src/thegent/agents/maif_runner.py
src/thegent/agents/codex_proxy.py (2 imports)
```

Requires logic changes (replace pareto_router/task_router/route_executor calls with CLIProxy).

### TODO Marks for LiteLLM (8 files, 30 min)
```
src/thegent/agents/codex_proxy.py
src/thegent/agents/droid.py
src/thegent/agents/direct_agents.py
src/thegent/cliproxy_adapter.py
src/thegent/mcp/server_runtime_helpers.py
src/thegent/mcp/server/lifecycle.py
```

Just add `# TODO(T1): migrate to CLIProxy` comments (streaming logic marked for T2).

### Internal Routing Wiring (3 files, 1-2 hours)
```
src/thegent/routing/auto_router.py
src/thegent/routing/pareto.py
src/thegent/routing/cost_aware_router.py
```

Update internal imports to use CLIProxy or stubs.

## Next Steps

1. **Read the docs** (5 min)
   - Main plan: `docs/research/ROUTING_MODULE_CLIPPROXY_MIGRATION_PLAN.md`
   - Quick reference: `docs/research/ROUTING_MIGRATION_CHECKLIST.md`

2. **Start with simple imports** (1-2 hours)
   - Pick a file from the "Simple Import Replacements" list
   - Replace import line: `thegent.routing.*` → `thegent.utils.*`
   - Verify no code changes needed
   - Test: `ruff check src/` and `tach check`

3. **Add TODO marks** (30 min)
   - Pick files from "TODO Marks for LiteLLM"
   - Add comment above streaming imports
   - Example: `# TODO(T1): migrate to CLIProxy (requires deeper streaming refactor)`

4. **Complex routing migrations** (3-6 hours)
   - Pick files from "Complex Routing Logic"
   - Follow file-specific instructions in checklist
   - Replace routing calls with CLIProxy HTTP calls
   - Test locally

5. **Internal wiring** (1-2 hours)
   - Update routing module's self-references
   - Use cliproxy_router or stubs as needed

6. **Delete & verify** (1 hour)
   ```bash
   rm -rf src/thegent/routing/
   grep -rn "from thegent.routing" src/ --include="*.py" | wc -l  # Must be 0
   pytest tests/test_pareto_router.py tests/test_race_orchestration.py -v
   tach check
   git commit -m "refactor(T1-cutover): migrate all routing callers to CLIProxy"
   ```

## Key Facts

- **No fallbacks:** If CLIProxy required, fail loudly
- **Compatibility layer:** Shims avoid massive refactoring
- **LiteLLM:** Marked TODO (T2) due to streaming complexity
- **Parallel:** Phases 3A/3B/3C can run in parallel
- **Timeline:** 6-12 hours (typically 1-2 days)

## Architecture

```
Before:
  callers → thegent.routing (11.5K LOC)

After:
  callers → thegent.utils (re-exports)
       ↓
       └→ thegent.routing (internal, marked TODO)
       └→ cliproxy_router.py
       └→ CLIProxy HTTP API (localhost:8317)
```

## Files at a Glance

| File | Purpose | Status |
|------|---------|--------|
| `src/thegent/cliproxy_router.py` | HTTP client wrapper | ✅ Ready |
| `src/thegent/utils/*.py` | Re-export shims | ✅ Ready |
| `docs/research/ROUTING_MODULE_CLIPPROXY_MIGRATION_PLAN.md` | Main plan | ✅ Ready |
| `docs/research/ROUTING_MIGRATION_CHECKLIST.md` | Implementation checklist | ✅ Ready |
| `docs/research/ROUTING_MIGRATION_STATUS.md` | Current status | ✅ Ready |
| All 22 caller files | To be migrated | ⏳ Pending |
| `src/thegent/routing/` | To be deleted | ⏳ Pending |

## Questions?

See `docs/research/ROUTING_MIGRATION_CHECKLIST.md` for:
- File-by-file instructions
- Code examples
- Common patterns
- Tips for implementation

Or `docs/research/ROUTING_MODULE_CLIPPROXY_MIGRATION_PLAN.md` for:
- Architecture details
- CLIProxy API spec
- Risk mitigation
- Success criteria
