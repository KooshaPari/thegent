# Architecture

## 2026-04-28 - Landing Pilot Architecture

**Project:** thegent
**Category:** ARCHITECTURE
**Status:** completed
**Priority:** P1

### Summary
`thegent/apps/landing` is the repo-owned project-plane surface for theGent.

### Key Decisions
- Keep the landing app inside the owning repo rather than treating it as a separate
  deployment island.
- Use `Taskfile.yml` as the canonical local control surface for install, dev, build,
  and preview.
- Make the Astro build offline-safe by degrading GitHub-backed content to committed
  snapshots.
- Keep `/preview/0` as the static no-open-PR fallback route.

### Current Shape
- `/` shows project metadata and README-backed landing content.
- `/docs` renders the docs microfrontend.
- `/qa` renders snapshot-backed quality panels when GitHub data is unavailable.
- `/otel` degrades loudly until an observability URL is configured.
- `/preview/<pr>` resolves preview deploys, with `/preview/0` as the fallback page.
