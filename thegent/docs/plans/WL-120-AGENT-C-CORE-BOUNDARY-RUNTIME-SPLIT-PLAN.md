# WL-120 Agent-C Plan: Core Boundary + Runtime Split

## Status
Blocked for direct implementation in this batch due scope (multi-week refactor). Implementation-ready decomposition prepared below.

## Phase A: Boundary Contract (1 day)
1. Author enforceable module boundaries.
- Files: `tach.toml`, `pyproject.toml`, `docs/governance/ARCHITECTURAL_GOVERNANCE.md`
- Zones:
  - `thegent.core` (policy-free execution primitives)
  - `thegent.runtime` (providers, routing, orchestration)
  - `thegent.surface` (CLI/MCP/UI)

2. Add import boundary checks in CI.
- Files: `.github/workflows/ci.yml`, `Taskfile.yml`
- Command: `tach check`

## Phase B: Monolith Strangler (2-3 days)
1. Split high-risk monoliths by seams first:
- `src/thegent/cli/commands/cli.py`
- `src/thegent/cli/commands/impl.py`
- `src/thegent/mcp/server.py`

2. Introduce facades to preserve command signatures during migration.

## Phase C: Runtime Surface Reduction (2-3 days)
1. Move non-core adapters out of startup-critical imports.
2. Lazy-load optional heavy modules behind explicit command paths.

## Phase D: Test Estate Rebalance (1-2 days)
1. Move integration-heavy tests out of default unit lane.
2. Keep fast core contract suite as default gate.

## Acceptance criteria
- Core package has explicit ownership and dependency contract.
- Startup path excludes non-core adapters by default import graph.
- LOC trend for `src/thegent/*.py` declines for 3 consecutive daily snapshots.

## Validation commands
- `python -m py_compile src/thegent/cli/commands/impl.py src/thegent/cli/commands/cli.py src/thegent/doctor.py`
- `pytest -q tests/test_wl116_audio_inputs.py tests/test_wl118_ollama_doctor_slice.py tests/test_wl119_grounding_sources.py`

## Wave-2 Delta (2026-02-21)
- Blocked sections and plan deltas:
  - Boundary policy enforcement spans CI, governance docs, and package ownership contracts not fully isolated to agent-c scope in this wave.
  - Keep WL-120 in phased mode; avoid partial boundary enforcement that could break concurrent branch work.
- Do-next proposal:
  - land boundary checker + config in a dedicated WL-120 branch with explicit owner approval from governance maintainers.
  - wire non-blocking CI report mode first, then switch to hard gate after baseline is clean.

## Wave-3 Execution Checklist (2026-02-21)
- [x] `src/thegent/bench/runner.py` + `src/thegent/cli/apps/bench.py`: add minimal `thegent bench run` wiring and persist one row.
- [x] `src/thegent/cli/apps/run.py` + `tests/test_wl116_run_audio_cli_wiring.py`: validate `--audio` forwarding in the foreground run harness path.
- [x] `src/thegent/doctor.py` + `src/thegent/routing/provider_types.py`: strengthen Ollama provider detection and user-facing remediation.
- [x] `src/thegent/cli/commands/impl.py` + `src/thegent/execution.py`: propagate grounding sources into finish-event logging payload.
- [x] `tests/test_wl115_bench_cli.py`, `tests/test_wl118_ollama_doctor_slice.py`, `tests/test_wl119_grounding_sources.py`, `tests/test_unit_provider_types.py`: add focused regression coverage for these slices.

## Wave-10 Checkpoint (2026-02-21)
- [x] WL-115 usability slice: normalize benchmark harness selector matching for mixed-case persisted rows.
- [x] WL-116 output slice: singular/plural transcript character grammar in CLI summary (`1 char`).
- [x] WL-118 output slice: actionable-hint dedupe normalization includes trailing punctuation variants.
- [x] WL-119 output slice: grounding source dedupe normalization handles case/punctuation URL variants.
- [x] WL-120 checkpoint slice: modernization master plan ledger expanded with wave-10 entries and state notes.
