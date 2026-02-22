# WL-128 Python Toolchain Deduplication - Slice Plan

## Scope

Reduce overlapping Python tooling surfaces with a bounded first slice that does not destabilize quality lanes.

## Current Overlap Targets

1. File watching pathways (`watchdog` direct usage vs shared fast watcher).
2. Parser/checker wrappers with duplicate behavior.
3. Repeated lint/test orchestration aliases that hit the same underlying commands.

## Slice Deliverables

1. Keep one canonical watcher abstraction per runtime path (`FastFileWatcher`).
2. Audit duplicate parser/checker entry points and map to one preferred implementation.
3. Add a small dedup report to modernization tracking and tie each remaining duplicate to a follow-up WL.

## Acceptance Criteria

1. Each concern has exactly one preferred implementation path documented.
2. Duplicate paths are either removed or explicitly tagged as temporary with owner and sunset WL.
3. No regression in existing quality/test commands.

## Dependencies

- Blocked by `WL-123` for full deprecation enforcement.
- Can proceed incrementally with non-breaking path unification.

## Closeout (2026-02-21)

1. Canonical quality path is now `task quality`; duplicate `quality_project`/`gate` task aliases were removed.
2. Canonical fast type lane is now `task typecheck`; duplicate `lint:type` alias was removed.
3. Deprecated quality aliases (`quality-a*`, `quality-fix*`) were removed and strict alias enforcement is active in the canonical quality lane via `task quality:deprecated-aliases:strict`.
4. Regression coverage was extended in `tests/test_wl128_toolchain_dedup.py` and `tests/test_wl123_deprecated_quality_aliases.py`.

## Wave-2 Progress (2026-02-21, B90-W2-C1/C2)

Implemented during B90 Wave-2 agent-c execution:

1. **B90-W2-C1 (test:cov removal)**: `test:cov` task in `Taskfile.yml` removed — it was identical to `test:` (`uv run pytest -q` with no `--cov` flag), making it a dead duplicate with a misleading description.
2. **B90-W2-C2 (quality-fix-agent.sh normalization)**: `scripts/quality-fix-agent.sh` `_run_fix()` function updated to delegate to `task format` for the safe (non-unsafe) fix path, eliminating redundant direct `uv run ruff` invocations in scripts.
3. **Tests added**: `tests/test_wl128_toolchain_dedup.py` — 11 tests covering pyproject.toml structure invariants and Taskfile canonical entrypoint presence. All 11 pass.

Remaining for Wave-3 (B90-W3-C1):
- Audit remaining `quality-a*`/`quality-fix*` alias tasks for full deprecation cleanup once strict enforcement is confirmed stable.
- Verify deterministic toolchain bootstrap end-to-end.
