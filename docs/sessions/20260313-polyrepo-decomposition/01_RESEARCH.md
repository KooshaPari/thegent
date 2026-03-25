# Research

## Structural Evidence
- Duplicate path pairs detected between `src/thegent/*` and `packages/thegent-*/*`: `TOTAL_DUP_PAIRS=998`.
- High-risk mirrored examples:
  - `src/thegent/commands/sync.py` and `packages/thegent-cli/src/thegent_cli/commands/sync.py`
  - `src/thegent/audit/shadow_audit_git.py` and `packages/thegent-audit/src/thegent_audit/audit/shadow_audit_git.py`
  - `src/thegent/integrations/workstream_autosync_shared.py` and `packages/thegent-sync/src/thegent_sync/integrations/workstream_autosync_shared.py`
  - `src/thegent/protocols/jsonrpc_agent_server.py` and `packages/thegent-protocols/src/thegent_protocols/protocols/jsonrpc_agent_server.py`
  - `src/thegent/agents/codex_proxy.py` and `packages/thegent-agents/src/thegent_agents/agents/codex_proxy.py`
  - `src/thegent/cliproxy_adapter.py` and package-side agent variants
  - `src/thegent/agents/unified_session_index.py` and package-side agent variants

## Largest Offenders
- `crates/thegent-hooks/src/main.rs` - 5514 lines
- `packages/thegent-cli/src/thegent_cli/apps/project.py` - 2013 lines
- `crates/thegent-shm/src/lib.rs` - 1987 lines
- `src/thegent/commands/sync.py` - 1654 lines
- `packages/thegent-cli/src/thegent_cli/commands/sync.py` - 1654 lines
- `src/thegent/cli/services/run_execution_core_helpers.py` - 1624 lines
- `packages/thegent-cli/src/thegent_cli/cli/services/run_execution_core_helpers.py` - 1624 lines
- `src/thegent/audit/shadow_audit_git.py` - 1479 lines
- `packages/thegent-audit/src/thegent_audit/audit/shadow_audit_git.py` - 1479 lines
- `src/thegent/protocols/jsonrpc_agent_server.py` - 1379 lines

## Placeholder / Partial Feature Evidence
- `src/thegent/integrations/workstream_autosync.py` is currently a stub module.
- `src/thegent/autosync/cycle.py` still routes through `_sync_to_github`, `_sync_from_github`, `_sync_to_linear`, `_sync_from_linear` placeholder flows.
- `src/thegent/commands/sync.py` contains placeholder reporting around board sync and `_perform_board_sync`.
- Multiple `src/thegent/integrations/*.py` modules are stub files rather than implemented adapters.

## Architectural Interpretation
The repo is already partially split by package name, but the split is not authoritative because `src/thegent` remains a shadow monolith. The right move is not another internal refactor. The right move is to make one tree authoritative per bounded context, then extract by runtime boundary.
