# Phenotype ecosystem architecture index

**Purpose:** Single entry page linking **governance**, **standards**, and **key repos** for navigation and onboarding.

## Governance (org-wide)

| Document | Location |
|----------|----------|
| Architectural governance (hexagonal, polyrepo, xDD) | `thegent/docs/governance/23_ARCHITECTURAL_GOVERNANCE.md` (canonical copy in thegent) |
| Polyrepo naming & productization | `docs/governance/POLYREPO_PACKAGE_NAMING_AND_PRODUCTIZATION.md` |
| Package inventory & rename backlog | `docs/governance/PHENOTYPE_PACKAGES_INVENTORY_AND_RENAME_BACKLOG.md` |
| Plugin contract template | `docs/governance/plugin_contract_template.md` |
| Worktree path policy | `docs/governance/worktree-path-policy.md` |
| xDD methodology catalog | `docs/governance/xdd-methodology-catalog.md` |
| Rolling hand rules | `docs/governance/rolling-hand-rules.md` |
| Release branch governance | `docs/governance/release-branch-governance.md` |
| ADRs | `docs/governance/adrs/` |

## Hub workspace

| Item | Path |
|------|------|
| Repos hub | `Phenotype/repos/` |
| Polyrepo productization wave | `docs/changes/polyrepo-productization-wave/` |
| Worklog (hub) | `worklog.md` |

## Representative repos (illustrative)

| Area | Examples |
|------|----------|
| Orchestration / CLI | `thegent`, `heliosCLI` |
| Apps | `heliosApp`, `AgilePlus` |
| APIs / agents | `agentapi-plusplus` |
| Docs / design | `phenodocs`, `phenotype-design` |
| Shared kits | `phenotype-go-kit`, `phenotype-config`, `template-commons/*` |

## Forge (headless agent)

| Doc | Path |
|-----|------|
| In-repo | `thegent/docs/guides/FORGE_HEADLESS.md` |
| Skill (workstation) | `~/.claude/skills/forge-agent/SKILL.md` |

---

**Maintenance:** Update this index when adding a new **org-wide** governance doc or retiring one (move to `.archive/` with a stub link).
