# WL-125 Monolith Split Plan: `src/thegent/cli/commands/impl.py`

## Status

Blocked by `WL-121`. This is an implementation-ready extraction plan.

## Goal

Split `impl.py` by service domain with stable callable contracts and unchanged CLI semantics.

## Target Module Layout

1. `src/thegent/cli/services/workstream_service.py`
2. `src/thegent/cli/services/governance_service.py`
3. `src/thegent/cli/services/session_service.py`
4. `src/thegent/cli/services/routing_service.py`
5. `src/thegent/cli/services/system_service.py`
6. `src/thegent/cli/commands/impl.py` (compat facade + orchestrator)

## Sequenced Slices

1. Extract pure stateless helpers first.
2. Extract stateful service blocks with constructor-based dependency wiring.
3. Keep `impl.py` function signatures stable while delegating internally.
4. Remove direct business logic from `impl.py` after parity confirmation.

## Contract Rules

1. Keep return payload keys unchanged.
2. Keep error text semantics stable for tests that assert strings.
3. Keep existing tracing tags and hooks in place.

## Validation Commands

1. `pytest -q tests/test_unit_cli_impl_pre_work_gate.py`
2. `pytest -q tests/test_unit_cli_impl_dag.py`
3. `pytest -q tests/test_unit_cli_impl_final_gaps.py`
4. `python -m py_compile src/thegent/cli/commands/impl.py`

## Done Criteria

1. `impl.py` is reduced to compatibility delegation.
2. Domain logic resides in `src/thegent/cli/services/*`.
3. Existing CLI implementation test suites pass without behavior drift.

## Wave-2 Dependency-Unblock Slice (2026-02-21)

1. Added baseline collector `scripts/collect_wl_monolith_baselines.py` and included `impl.py` in the tracked target set.
2. Captured `impl.py` extraction metrics (line/function/class/async counts) to provide measurable reduction targets per future split PR.
3. Shared unblock artifact path:
   - `.thegent/agent-batch/wave2-monolith-baseline.json`
