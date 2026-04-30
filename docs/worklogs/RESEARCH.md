# Research

## 2026-04-28 - Landing Pilot Baseline

**Project:** thegent
**Category:** RESEARCH
**Status:** completed
**Priority:** P1

### Summary
Validated the `thegent/apps/landing` pilot as the current baseline for the
org/project-plane consolidation work.

### Key Findings
- `thegent/Taskfile.yml` now exposes `landing:install`, `landing:dev`,
  `landing:build`, and `landing:preview`.
- The landing app is Astro-based and lives under `apps/landing`.
- Static build generation must degrade cleanly when GitHub is unreachable.

### Next Steps
- [ ] Use the pilot contract as the reference for any future landing imports.
- [ ] Keep the remaining product landing repos in the standalone lane unless a new
      repo-specific decision changes the path.
