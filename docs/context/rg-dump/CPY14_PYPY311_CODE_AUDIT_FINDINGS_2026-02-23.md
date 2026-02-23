# CPython 3.14 / PyPy 3.11 Code Audit Findings

Date: 2026-02-23
Scope: `thegent`, `agentapi++`, `contracts/provider-bridge`
Method: static code/config scan against CPy14/PyPy311 feature checklist.

## Critical Findings

1. Hard interpreter pin blocks runtime matrix support.
- File: `agentapi++/atomsAgent/pyproject.toml:10`
- Finding: `requires-python = "==3.12.*"`
- Impact: prevents CPython 3.14 and PyPy 3.11 support by policy.
- Action: widen to matrix-compatible range (for example `>=3.11,<3.15`) after dependency validation.

## Important Findings

1. Direct `__annotations__` access should move to annotationlib-safe path for 3.14-oriented auditing.
- Files:
  - `thegent/src/thegent/adapters/acp_mcp_bridge.py:347`
  - `thegent/src/thegent/utils/reusable_helpers.py:38`
- Finding: raw `func.__annotations__` reads.
- Impact: fragile under deferred annotation semantics and runtime annotation resolution changes.
- Action: replace with robust helper using `annotationlib.get_annotations` when available, fallback safely.

2. Widespread `from __future__ import annotations` usage across active codebases.
- Files: many across `thegent/src/*`, `agentapi++/atomsAgent/src/*`, `contracts/provider-bridge/*`.
- Finding: pervasive future-import pattern.
- Impact: not broken now, but this pattern should be strategically reduced as 3.14+ annotation behavior stabilizes and deprecation timeline advances.
- Action: prioritize modules that rely on runtime annotation introspection and migrate first.

3. Structured concurrency modern primitives are underused in active paths.
- Query: no hits for `TaskGroup` / `asyncio.timeout(` across scanned active source paths.
- Impact: weaker auditability for cancellation/failure fan-out and timeout semantics.
- Action: adopt `TaskGroup` in fan-out orchestration sites and `asyncio.timeout` for deadline-sensitive sections.

## Medium Findings

1. Cancellation swallowing patterns exist and should be explicitly categorized.
- Files:
  - `agentapi++/atomsAgent/src/atomsAgent/services/fastmcp_oauth_refresh.py:72`
  - `agentapi++/atomsAgent/src/atomsAgent/sandbox/pool.py:67`
  - `agentapi++/atomsAgent/src/atomsAgent/sandbox/pool.py:168`
  - `thegent/src/thegent/integrations/workstream_autosync.py:834`
  - `thegent/src/thegent/integrations/workstream_autosync.py:845`
  - `thegent/src/thegent/orchestration/unified_worker.py:68`
- Finding: `except asyncio.CancelledError: pass` appears mostly in shutdown/stop code paths.
- Impact: often valid for graceful shutdown, but should be codified so cancellation isn’t accidentally swallowed in business logic.
- Action: add lint/audit rule: allowed in lifecycle stop/cleanup sections only; otherwise re-raise.

2. `uv run` at workspace root can trigger unrelated editable-build failures.
- Evidence from prior test execution in this session.
- Impact: cross-project audit/test workflows become noisy.
- Action: for scoped audits/tests, standardize `uv run --no-project --with ...` in tooling docs/scripts.

## Positive Findings

1. Existing interpreter-aware dependency split is already in place in `thegent`.
- File: `thegent/pyproject.toml:65-66`
- `ujson` for PyPy and `orjson` for CPython via environment markers.
- Value: good baseline pattern for dual-runtime optimization.

2. `contracts/provider-bridge` scaffold is mostly runtime-portable.
- Files under `contracts/provider-bridge/schema/*`, `contracts/provider-bridge/types/*`, `contracts/provider-bridge/tests/*`
- Value: strict schemas + pure Python/Go interface scaffolding supports interpreter-agnostic core contract design.

## Priority Remediation Plan

Phase 1 (immediate)
1. Relax `agentapi++` Python pin to support matrix target.
2. Introduce shared annotation helper and replace direct `__annotations__` access in flagged files.
3. Add policy note/lint rule for allowed `CancelledError` swallowing locations.

Phase 2 (short term)
1. Add interpreter matrix test lanes for CPython 3.14 and PyPy 3.11 in active repos.
2. Introduce `TaskGroup`/`asyncio.timeout` in critical orchestration paths.

Phase 3 (hardening)
1. Reduce `from __future__ import annotations` where no longer needed.
2. Add audit checks for deprecated APIs and annotation/runtime assumptions.

## Quick Commands to Continue Audit

```bash
rg -n "requires-python" thegent/pyproject.toml agentapi++/atomsAgent/pyproject.toml
rg -n "__annotations__" thegent/src agentapi++/atomsAgent/src
rg -n "except asyncio\.CancelledError:" thegent/src agentapi++/atomsAgent/src
rg -n "TaskGroup|asyncio\.timeout\(" thegent/src agentapi++/atomsAgent/src
```
