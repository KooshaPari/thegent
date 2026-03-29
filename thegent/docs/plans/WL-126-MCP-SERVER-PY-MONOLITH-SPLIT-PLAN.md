# WL-126 Monolith Split Plan: `src/thegent/mcp/server.py`

## Status

Blocked by `WL-121`. This plan is implementation-ready for immediate execution after boundary ratification.

## Goal

Split MCP server responsibilities into bounded modules (transport/auth/router/tool-registry) with stable public behavior.

## Target Module Layout

1. `src/thegent/mcp/server/transport.py`
2. `src/thegent/mcp/server/auth.py`
3. `src/thegent/mcp/server/router.py`
4. `src/thegent/mcp/server/tool_registry.py`
5. `src/thegent/mcp/server/serialization.py`
6. `src/thegent/mcp/server.py` (compat bootstrap + exports only)

## Sequenced Slices

1. Extract serialization/types first (low coupling).
2. Extract tool registry and static tool wiring.
3. Extract transport lifecycle and startup.
4. Extract auth and routing orchestration.
5. Reduce `server.py` to bootstrap/composition only.

## Contract Guardrails

1. Preserve tool names and schema fields.
2. Preserve error response envelope shape.
3. Preserve startup/shutdown behavior and health endpoints.

## Validation Commands

1. `pytest -q tests/mcp/test_context_api.py`
2. `pytest -q tests/mcp/test_tool_patterns.py`
3. `pytest -q tests/test_unit_mcp_server_coverage_e.py`
4. `pytest -q tests/test_unit_mcp_server_deep.py`

## Done Criteria

1. `server.py` is reduced to bootstrap-level composition.
2. MCP responsibilities are split into stable modules under `src/thegent/mcp/server/`.
3. Existing MCP tests pass with no API behavior drift.

## Wave-2 Dependency-Unblock Slice (2026-02-21)

1. Added `scripts/collect_wl_monolith_baselines.py` and wired `src/thegent/mcp/server.py` as a tracked monolith target.
2. Captured baseline metrics for server extraction sequencing (line count, top-level callables, async/class distribution, command decorators where applicable).
3. Shared unblock artifact path:
   - `.thegent/agent-batch/wave2-monolith-baseline.json`
