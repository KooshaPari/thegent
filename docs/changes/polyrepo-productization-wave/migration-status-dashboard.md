# Migration status dashboard — polyrepo productization

**Updated:** 2026-03-26 (rolling)  
**Source plan:** `proposal.md`, `tasks.md`

## Phase status

| Phase | Theme | Status |
|-------|--------|--------|
| P1 | Discovery & classification | **In progress** — inventory doc exists; classification ongoing |
| P2 | Architecture contracts | **Started** — plugin template, worktree policy |
| P3 | Libification | **Planned** — rename backlog in governance |
| P4 | Service/plugin split | **Planned** |
| P5 | Verification & Pages | **Blocked** — Actions billing on some orgs |

## Workstream checklist (weekly)

| Check | Owner | Last run |
|-------|--------|----------|
| Rename backlog reviewed | Platform | — |
| Duplicate `phenotype-*` clusters triaged | Platform | — |
| Forge / thegent skill docs synced | DevEx | — |
| `PHENOTYPE_ECOSYSTEM_ARCHITECTURE_INDEX.md` links valid | DevEx | — |

## Blockers

| Blocker | Mitigation |
|---------|------------|
| GitHub Actions billing | Local quality gates; `gh pr merge --admin` when policy allows |
| `phenotype-infrakit` vs `phenotype-shared` dedup | ADR + single workspace decision |

## Completed / superseded

| Item | Notes |
|------|--------|
| PI-008 OCC regression | `thegent` PR #763 merged |
| Local docs sync | `thegent` PR #766 |
| Forge headless skill | `~/.claude/skills/forge-agent/SKILL.md` + `thegent/docs/guides/FORGE_HEADLESS.md` |

---

**Next:** Fill “Last run” dates when executing weekly verification; link dependency graph CSV when generated.
