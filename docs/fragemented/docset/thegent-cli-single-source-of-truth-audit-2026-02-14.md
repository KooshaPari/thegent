# Thegent CLI Single Source of Truth Audit

**Date:** 2026-02-14
**Scope:** Ensure every capability is reachable via `thegent <subcommand>`; no hidden features only in scripts.
**Source:** FastMCP Implementation Plan §4 Phase 1 prerequisite

---

## Audit Criteria

1. **No Makefile targets** that wrap or bypass the CLI for thegent capabilities.
2. **No scripts** that invoke thegent internals (e.g. `run_impl`, `_ensure_config`) instead of CLI commands.
3. **All docs** use `thegent run`, `thegent bg`, etc. — never legacy `thegent <agent> <prompt>` (prompt-first is canonical).

---

## Findings

### Entry Points

| Entry | Path | Status |
|-------|------|--------|
| CLI | `pyproject.toml` → `thegent = "thegent.main:app"` | ✓ Single entry point |
| MCP | `thegent serve` (via main app) | ✓ CLI subcommand |
| Process-compose MCP | `python -m thegent.main serve` | ✓ Uses CLI entry |
| Process-compose proxy | `scripts/start_proxy.py` | ✓ Python-native |

### Scripts Audited

| Script | Before | After |
|--------|--------|-------|
| `scripts/start_proxy.py` | Legacy shell wrapper | Pure Python startup + `os.execv` |
| `scripts/ensure-cliproxy-config.py` | CLI subprocess wrapper | Direct Python `_ensure_config(settings)` call |

### Makefile

- **None found** in thegent repo. ✓

### Docs

- README, PROVIDER_SETUP_GUIDE, SKILL.md, plans: all use `thegent run`, `thegent bg`, `thegent ps`, etc. ✓
- Prompt-first syntax (`thegent run "prompt" [agent]`) is canonical; agent optional when `-M` given. ✓

### Tests

- Unit tests (e.g. `test_agent_sync_async_validation.py`) import `run_impl` directly — **acceptable** for testing the impl layer in isolation.
- E2E tests use `CliRunner` and invoke `app` (CLI). ✓

---

## Remediation Applied

1. **start-proxy.sh removed:** replaced by `scripts/start_proxy.py` (Python-native, no shell wrapper).
2. **ensure-cliproxy-config.py:** replaced CLI subprocess invocation with direct Python config call.

---

## Verification

```bash
# Ensure config
python scripts/ensure-cliproxy-config.py

# Start proxy in foreground
python scripts/start_proxy.py
```

---

## Status

**Audit complete.** All thegent capabilities are now reachable via the CLI. No scripts or Makefile targets bypass the CLI for orchestration/config capabilities.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
