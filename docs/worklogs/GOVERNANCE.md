# Governance

## 2026-04-28 - Landing Pilot Governance

**Project:** thegent
**Category:** GOVERNANCE
**Status:** completed
**Priority:** P1

### Summary
The landing pilot now has a repo-local operational contract that matches the
org/project-plane consolidation plan.

### Policy Notes
- Keep generated assets out of source control: `node_modules`, `dist`, `.astro`, and
  `.vercel` remain ignored.
- Treat network access as optional at build time. If GitHub cannot be reached, the
  build must still succeed with snapshot fallbacks.
- Keep route contracts explicit and honest. The no-PR preview fallback is `/preview/0`,
  not a placeholder slug.

### Validation
- `task landing:build` passes in the current repo state.
- The build emits loud degraded states for GitHub-backed content when offline.
- The repo-local landing task wrappers are now the canonical entry point for local use.
