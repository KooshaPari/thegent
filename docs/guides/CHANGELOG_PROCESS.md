# Changelog Process

This repository uses [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format with Semantic Versioning release tags.

## Source of Truth

- Root changelog file: `CHANGELOG.md`
- Draft section for upcoming changes: `## [Unreleased]`

## Required Workflow

1. For every user-visible change, add an entry under `## [Unreleased]` in `CHANGELOG.md`.
2. Place entries under a Keep-a-Changelog type section:
   - `### Added`
   - `### Changed`
   - `### Deprecated`
   - `### Removed`
   - `### Fixed`
   - `### Security`
3. Keep entries short, concrete, and scoped to observable behavior.
4. Include references to notable files/modules when useful.
5. Do not move items out of `Unreleased` until creating a release section.

## Releasing

1. Create a new version heading in `CHANGELOG.md`:
   - `## [X.Y.Z] - YYYY-MM-DD`
2. Move relevant items from `Unreleased` into that version section.
3. Recreate empty type buckets under `Unreleased` for ongoing work.
4. Verify `task changelog:check` passes.

## Validation

Run:

```bash
task changelog:check
```

This check fails if `CHANGELOG.md` is missing the `## [Unreleased]` section.

## Entry Template

Use the repository template:

- `docs/reference/CHANGELOG_ENTRY_TEMPLATE.md`
