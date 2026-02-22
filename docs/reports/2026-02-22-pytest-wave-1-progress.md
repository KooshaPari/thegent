# Wave-1 Progress (Execution)

## Completed by Codex
- Added `scripts/test_pytest_wave_artifacts.py` with three commands:
  - `collect`
  - `trace-scan`
  - `heavy-untagged`
- Added cross-repo Atoms clean/deploy KB and canonical deploy guidance in
  `docs/contracts/ATOMS_CLEAN_DEPLOY_KNOWLEDGE_BASE.md` (Tasks 81–83).
- Added pytest health observability surface in `thegent/scripts/test_pytest_wave_artifacts.py`:
  - `health` aggregation command
  - `task test:health`
  - `task test:pr-gate` now writes `artifacts/pytest/health/pr-gate.json` and `.../pr-gate.md`
  - CI alert printing + dedicated health artifact upload
  - Tasks 84–85
- Completed Wave-1 task block 66-70 scaffolding in `scripts/pytest_wave_perf_orchestrator.py`:
  - `collect-tests` command for deterministic node-id collection artifacts.
  - `xdist` crash-detected fallback artifacts (`command_fallback`, `crash_signals`, `return_code`).
  - `testmon-pilot` with cache versioning/TTL pruning and fallback-required signal.
  - `testmon-evaluate` output with `estimated_miss_rate`, `estimated_missed_tests`, and `recommended_fallback`.
  - `shard-plan` contract fields (`formula`, `assignment_schema`, input schema metadata).
- Updated `Taskfile.yml` with Wave-1 execution helpers:
  - `task test:collect:baseline`
  - `task test:collect:fast-gate`
  - `task test:trace:scan`
  - `task test:trace:untagged-heavy`
  - `task test:pr-gate`
  - `task test:collect:wave`
  - `task test:wave:xdist`
  - `task test:wave:testmon-pilot`
  - `task test:wave:testmon-evaluate`
  - `task test:wave:shard-plan`
- Added `pytest-testmon` to `pyproject.toml` dev dependency for pilot command execution.
- Updated CI workflow commands to use gated pytest profile:
  - `.github/workflows/test.yml` now runs `task test:collect:fast-gate` + `task test:fast-lane`
  - `.github/workflows/ci.yml` test job now runs `task test:collect:fast-gate` + `task test:fast-lane`

## Outstanding (Wave-1)
- Promote `test:collect:fast-gate` failure mode from hard fail to informational in builds where legacy collection blockers are still triaged.
- Add markdown summaries for `test_pytest_wave_artifacts.py` outputs for PR readability.
- Agent-2/3/4/5/6 workstreams (P0 stabilization, FR extractor, DAG execution, gating, and observability) remain pending in this repository branch.

## Acceptance Review
1. `task test:collect:baseline` produces JSON at `artifacts/pytest/baseline/collect.json`.
2. `task test:pr-gate` runs without side effects and writes at least:
   - `artifacts/pytest/baseline/fast-gate.json`
   - `artifacts/pytest/traceability/traceability-links.json`
   - `artifacts/pytest/traceability/untagged-heavy-tests.json`
3. CI still publishes existing test artifacts and remains deterministic.
4. Task-66: `task test:wave:xdist` stores deterministic safeguards artifact with crash signals and fallback status.
5. Task-67: `task test:wave:testmon-pilot` writes hit-rate, miss-rate band, fallback-required, and cache-prune metadata.
6. Task-68: `testmon` cache artifacts are isolated to `.../.cache/thegent/pytest/testmon/v1/` and prune by `--cache-ttl-days`.
7. Task-69: `task test:wave:testmon-evaluate` emits `recommended_fallback`, `estimated_missed_tests`, and `fallback_risk`.
8. Task-70: `task test:wave:shard-plan` emits `schema_version`, `formula`, `assignment_schema`, and deterministic shard assignment arrays.
9. Task-81: `docs/contracts/ATOMS_CLEAN_DEPLOY_KNOWLEDGE_BASE.md` captures cross-repo clean/deploy baselines and canonical path guidance.
10. Task-82: The same knowledge base documents canonical clean/deploy path and deprecated alternatives.
11. Task-83: Env-discovery precedence contract for `atoms` flows is explicit in the knowledge base and implementation references.
12. Task-84: `task test:health` runs and writes `artifacts/pytest/health/pr-gate.{json,md}` with severity alerts.
13. Task-85: PR CI workflows emit health alert summaries and upload a dedicated `pytest-health-*` artifact.
