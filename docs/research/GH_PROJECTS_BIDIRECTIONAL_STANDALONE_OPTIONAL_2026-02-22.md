# GitHub Projects Bidirectional Sync (Standalone Optional) — 2026-02-22

## Goal

Enable thegent to synchronize work bidirectionally with GitHub Projects while remaining optional and standalone-safe:

- Optional: disabled by default.
- Standalone-safe: no hard dependency on GitHub APIs when disabled.
- Bidirectional: local workstream/worklog state can push to GitHub Projects and pull updates back.

## Scope

- Source of truth remains local (`docs/reference/WORK_STREAM.md`) unless explicit sync is invoked.
- Support import/export against Project v2 using `gh` CLI.
- Preserve source-to-solution traceability fields:
  - Board ID
  - Source Kind/Repo/Ref/URL
  - Status/Priority/Wave/Effort/Theme

## Proposed Config (thegent)

Environment and config toggles:

- `THGENT_GH_PROJECT_SYNC_ENABLED=0|1` (default: `0`)
- `THGENT_GH_PROJECT_OWNER=<org-or-user>`
- `THGENT_GH_PROJECT_NUMBER=<project-number>`
- `THGENT_GH_PROJECT_DIRECTION=pull|push|both` (default: `both`)
- `THGENT_GH_PROJECT_STANDALONE_MODE=1` to run sync tooling without thegent runtime dependencies.

## Command Surface

- `thegent project sync --direction pull`
- `thegent project sync --direction push`
- `thegent project sync --direction both`
- `thegent project export --format csv --output <path>`
- `thegent project import --input <csv>`

## Data Mapping

Local -> GitHub Project fields:

- `Title` <- work item title
- `Status` <- status
- `Priority` <- priority
- `Wave` <- wave
- `Effort` <- effort
- `Theme` <- theme
- `Board ID` <- stable board/workstream id
- `Body` <- source mapping + implementation note + evidence links

GitHub Project -> Local:

- Pull status/priority assignments and update matching `Board ID` rows.
- For missing local items, append to a staging section for review before merge.

## Conflict Policy

- If both sides changed same field after last sync:
  - default policy: local wins, record conflict note.
  - optional policy: `--policy remote-wins`.
- Always write sync report artifact with changed rows and conflicts.

## Acceptance Criteria

- Sync commands are no-op clean when feature disabled.
- Push updates at least Status + Priority + Body mapping fields.
- Pull updates from Project and stage into local workstream update queue.
- Standalone mode can run with only `gh` auth + local files.

## Immediate Follow-up Items

1. Add config fields in thegent settings layer.
2. Add project-sync service module and CLI commands.
3. Add smoke tests for disabled mode, push-only, pull-only, and both.
4. Add docs linking this flow from thegent and cliproxy board docs.
