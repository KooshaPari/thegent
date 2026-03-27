# ADR-0008: Release Channel Branch Strategy

## Status
Accepted — 2026-03-27

## Context
Previously all repos used `main` as the sole integration and release branch. This provided no mechanism for staged promotion (alpha → beta → stable), making it impossible to separate in-progress integration from production-ready code.

## Decision
All active repos adopt a three-channel release branch strategy on top of `main`:

| Branch | Channel | Purpose |
|--------|---------|---------|
| `main` | nightly | Development integration, all PRs target here |
| `releases/alpha` | alpha | Features cleared for alpha testing |
| `releases/beta` | beta | Alpha-validated builds promoted for broader testing |
| `releases/stable` | stable | Beta-validated, production-ready artifacts |

### Promotion Flow

```
feature/* → main → releases/alpha → releases/beta → releases/stable
```

Promotion between channels is always via PR (no direct push to `releases/beta` or `releases/stable`).

### Branch Protection Rules

- `releases/stable`: PR required, stale review dismissal enabled, all merges squash
- `releases/beta`: PR required
- `releases/alpha`: PR required
- `main`: Direct push permitted for admins; PRs required for contributors

### Initial Setup (2026-03-27)

All three branches created at `main` HEAD in the following repos:
heliosApp, AgilePlus, heliosCLI, portage, thegent, bifrost-extensions, phenotype-shared, clikit, trace, cliproxyapi-plusplus, agent-wave, parpour, phenotype-infrakit, phenotype-go-kit, tokenledger

## Consequences

- Release branches must be promoted deliberately via PR
- CI/CD pipelines should be channel-aware (deploy `releases/stable` to production, `releases/beta` to staging, `releases/alpha` to alpha env)
- Hotfixes targeting production must be cherry-picked into `releases/stable` AND backported to `main`
- Dependabot/Renovate PRs always target `main`

## heliosCLI Location Note

heliosCLI currently exists as a standalone canonical clone at `repos/heliosCLI/` rather than `repos/apps/heliosCLI/`. This is an anomaly vs. other apps in `repos/apps/` (`AgilePlus`, `heliosApp`, `helMo`). heliosCLI has its own GitHub remote (`KooshaPari/heliosCLI.git`) and is not a submodule of any other package. Future work: relocate to `repos/apps/heliosCLI/` when convenient and update all worktree paths and submodule references accordingly.

## Alternatives Considered

- **Single main branch (status quo)**: Simple but prevents staged rollouts
- **Git Flow (develop/release/hotfix)**: More complex; release channel model is simpler for an agent-driven environment
- **Feature flags only**: Orthogonal; does not address branch-based release gating
