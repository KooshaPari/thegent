# 12_NEXT_WAVE_F — next 24 items (6 × 4)

**Follows** `07`–`11`. **Snapshot:** 2026-03-24. **Inventory:** skip unless a dedicated inventory session. **Six slices** map to parallel work (optional one agent per slice).

## Slice 1 — Roadmap & prioritization (4)

1. Re-rank **blocker matrix** families by **business risk** (not just dirty count).
2. **Quarterly** worktree debt budget: max N lanes touched per month.
3. **Dependency upgrades** plan (major versions): schedule, not ad hoc.
4. **Sunset** list: repos or lanes marked for archive with dates.

## Slice 2 — Knowledge & continuity (4)

5. **Bus factor** check: critical paths (secrets, PTY) have **second reviewer** on file.
6. **Runbook** index: link ENOSPC, worktree prune, and CI failure from one place.
7. **Decision log** entry for major splits (PTY, secrets tests)—ADR or short note.
8. **Lunch-and-learn** or internal doc: **optional**; skip if no audience.

## Slice 3 — Risk & resilience (4)

9. **Backup** of signing keys / release credentials—verify off-site copy exists (process).
10. **Disaster recovery** drill: clone repo fresh, `bun install`, run tests (time-boxed).
11. **Secrets rotation** policy: if credential store rotates, calendar reminder.
12. **Blast radius**: document which repos share a single `node_modules` or cache.

## Slice 4 — Engineering excellence (4)

13. **Definition of Done** for worktree work: clean `git status`, green CI, docs updated.
14. **Code review** checklist: security, tests, file size, no silent fallbacks.
15. **Pairing** on high-risk merges (optional but recommended for crypto/PTY).
16. **Refactor** budget: 10–20% capacity for debt in next cycle.

## Slice 5 — Observability & feedback (4)

17. **Structured logging** review: correlation IDs on PTY events still consistent.
18. **Error taxonomy**: user-visible vs internal for new failure modes.
19. **User feedback** channel for CLI/runtime issues (issue template).
20. **Internal metrics** (if any): track merge frequency, CI duration trend.

## Slice 6 — Meta: queue health (4)

21. **Compress** waves 07–12 if items become redundant—merge into one “active” backlog file.
22. **Version** the wave files (e.g. date suffix) if multiple teams edit same folder.
23. **Automation** hook: optional script to emit “next 24” from git status (future).
24. **Stop condition**: when worktree forest is **green**, **archive** this session pack to `docs/sessions/archive/`.

---

**Roles:** **Product / EM** (1–4), **Tech lead + docs** (5–8), **SRE + security** (9–12), **Eng standards** (13–16), **Observability / PM** (17–20), **Platform governance** (21–24).
