# Hexagonal Polyglot Repo Audit and Kitty Migration Spec

Created: 2026-06-05
Status: active planning
Scope: thegent, sharecli, owned Phenotype tooling, and registered client surfaces

## Purpose

Move owned workflow/spec tooling from Spec Kitty conventions into AgilePlus, then use the AgilePlus track to finish architecture, quality, and client readiness work for thegent and related owned tooling.

## Current Readiness Finding

This track is not complete until current validation evidence exists. The repository currently has AgilePlus directories and evidence logs, but the active spec was empty and `.kittify` still contains Spec Kitty commands, templates, and path conventions. That means the migration cannot be considered complete from present repo state.

The repo also has app/client surfaces under `apps/landing`, `web/dashboard`, `mobile/app`, and `apps/byteport`, plus Phenotype module manifests under `Phenotype/projects/modules`. These surfaces need explicit acceptance checks before they can be called polished, registered, and validated.

## Goals

- Replace owned Spec Kitty workflow entrypoints with AgilePlus equivalents.
- Preserve useful Kitty assets only as migrated AgilePlus templates, tasks, or archived reference material.
- Define SDD, BDD, and TDD traceability for active features before implementation is marked complete.
- Run and record quality gates with a reproducible toolchain, including missing-tool blockers.
- Audit thegent and sharecli for hexagonal, KISS, DRY, SOLID, and polyglot readiness.
- Validate desktop, web, and mobile/client surfaces against product readiness criteria.
- Ensure Phenotype registration includes the relevant thegent/sharecli apps and icon assets.

## Non-Goals

- No broad rewrite of generated assets without a corresponding AgilePlus work package.
- No claim of quality gate success from stale evidence.
- No client polish claim without build or runtime validation evidence.
- No cross-repo merge or PR cleanup without branch-specific review.

## Required Evidence

- `task quality` or equivalent component gate output.
- `task quality:full` or recorded blocker when repo tooling is unavailable.
- SDD requirements mapped to AgilePlus work packages.
- BDD scenarios mapped to user-visible workflows.
- TDD tests mapped to changed modules and acceptance criteria.
- Kitty-to-AgilePlus inventory showing migrated, archived, or removed assets.
- Client readiness report for web, desktop, mobile, and management UI surfaces.
- Phenotype registration report showing app/module manifest entries and icon files.

## Acceptance Criteria

- AC01: No owned workflow requires `.kittify`, `spec-kitty`, or `kitty-specs` as its primary path.
- AC02: Every active feature in this track has an AgilePlus work package with lane frontmatter.
- AC03: SDD, BDD, and TDD coverage matrices exist for thegent and sharecli readiness work.
- AC04: Quality gate status is current, with passing output or explicit environment blockers.
- AC05: Hexagonal/polyglot audit outputs identify boundaries, ports, adapters, coupling hotspots, and shared-contract risks.
- AC06: Web, desktop, and mobile/client surfaces have build or runtime validation evidence.
- AC07: Phenotype module registration includes relevant app entries and icon assets, including `.ico` where required by the target client.
- AC08: Final readiness cannot be declared until all work packages are in `done` and evidence is appended.

## Risks

- Legacy Kitty assets may encode useful behavior that needs migration rather than deletion.
- Quality gate tools may be unavailable on the current PATH, which must be treated as a blocker.
- Client directories may contain planning docs without runnable implementations.
- Phenotype manifests may register repos but not UI application entries or icon assets.
