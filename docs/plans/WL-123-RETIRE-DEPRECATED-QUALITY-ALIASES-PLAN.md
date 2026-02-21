# WL-123 Retire Deprecated Quality Aliases - Implementation Plan

## Status

Blocked by `WL-122` for canonical max-lines gate parity. This file captures implementation-ready steps for immediate execution once unblocked.

## Scope

Retire deprecated quality aliases while preserving one canonical quality entrypoint and parity for CI/local workflows.

## Deprecated Alias Set (Current)

1. `quality:full` (alias to `quality`)
2. `quality-a`, `quality-a-r`, `quality-a-h`
3. `quality-a-d`, `quality-a-d-h`
4. `quality-fix`, `quality-fix-d`, `quality-fix-a`, `quality-fix-a-d`, `quality-fix-a-h`, `quality-fix-a-d-h`

## Canonical Target Commands

1. `task quality`
2. `task quality:dag`
3. `task quality:dag:soft`
4. `task quality:dag:hard`
5. `task quality:fix:runner`

## Execution Steps

1. Remove deprecated aliases from `Taskfile.yml`.
2. Remove alias completions from `scripts/completion/thegent.bash` and `scripts/completion/thegent.zsh`.
3. Update docs references in:
   - `docs/guides/QUALITY_ASSURANCE.md`
   - `docs/reference/cli-examples.md`
4. Add migration notes to changelog/release notes.
5. Run focused validation and fix remaining references.

## Validation Commands

1. `task quality:dag:dry-run`
2. `rg -n "quality-a|quality-fix-a|quality:full" docs scripts Taskfile.yml`
3. `thegent --help`
4. `pytest -q tests/e2e/test_plan_commands.py`

## Done Criteria

1. Deprecated aliases are removed from active command surfaces.
2. CI and local quality runs pass through one canonical path.
3. No documentation references remain to removed aliases.

## Wave-2 Dependency-Unblock Slice (2026-02-21)

1. Added `scripts/check_deprecated_quality_aliases.py` to generate a deterministic alias inventory directly from `Taskfile.yml`.
2. Script supports staged enforcement:
   - baseline mode (`--strict` off): report-only for blocked state
   - enforcement mode (`--strict` on): fail once WL-122 is complete and alias removal is expected
3. Added unit coverage in `tests/test_wl123_deprecated_quality_aliases.py` to lock parser/report behavior before destructive alias removal work.
