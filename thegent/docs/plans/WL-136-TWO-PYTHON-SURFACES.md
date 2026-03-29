# WL-136 Two Python Surfaces (Core vs Tooling/Test)

## Objective

Split Python responsibility into two explicit surfaces:

1. Core runtime surface (must shrink aggressively).
2. Tooling/test/research surface (can remain broad but isolated from default fast lanes).

## Surface Definition

| Surface | Includes | Excludes |
|---|---|---|
| Core runtime | `src/thegent/cli/commands/*`, `src/thegent/mcp/*`, orchestration/governance runtime modules | test harnesses, docs tooling, one-off scripts |
| Tooling/test/research | `tests/*`, `scripts/*`, docs generators, migration utilities | runtime dispatch code paths used in production invocations |

## Rules

1. New runtime behavior lands in core modules only.
2. Tooling/test helpers cannot become runtime dependencies without explicit ADR.
3. Fast lane CI references core contracts first; tooling lanes run separately/nightly where feasible.

## Migration Slices

1. Tag current modules by surface in a directory map.
2. Move mixed-surface utilities behind explicit adapters.
3. Add CI lane mapping to guarantee core path remains bounded.

## Decision Record

- Ratified in `docs/reference/ADR-016-two-python-surfaces.md` (ACCEPTED, 2026-02-21).

## Exit Criteria

1. Core surface has decreasing LOC trend with no behavior regressions.
2. Tooling/test growth does not impact fast-lane runtime checks.
3. Each mixed module has a migration owner and target date.
