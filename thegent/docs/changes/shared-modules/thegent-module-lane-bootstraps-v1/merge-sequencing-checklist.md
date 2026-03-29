# Merge Sequencing Checklist (P6.33, P6.34, P6.44)

## Merge prerequisites

- Confirm branch/PR owner mapping in `lane-pr-anchor-map.md`.
- Confirm each PR is restricted to its module slice only.
- Confirm baseline smoke artifacts are attached to PR description.

## Sequencing order and verification

- Merge lane PRs in dependency order:
  1. `thegent-app`
  2. `thegent-mcp`
  3. `thegent-control-plane`
  4. `thegent-execution`
  5. `thegent-governance`
- After each merged PR:
  - Rerun `task lane:split:all-smoke`.
  - Record PR state and failing checks in merge-run log.

## Merge train target

- Proposed temporary train branch: `int/mod-split-stage-1`
- Final order gate: verify check matrix in `03_DAG_WBS.md` before advancing to the next PR.
