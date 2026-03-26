# Polyrepo Productization Wave Tasks

**Last updated:** 2026-03-26

## Status summary

| # | Task | Status | Artifact / note |
|---|------|--------|-----------------|
| 1 | Repo inventory `phenotype-bound` vs `market-neutral` | **Partial** | [PHENOTYPE_PACKAGES_INVENTORY_AND_RENAME_BACKLOG.md](../../governance/PHENOTYPE_PACKAGES_INVENTORY_AND_RENAME_BACKLOG.md) |
| 2 | Rename matrix | **Partial** | Same + Tier B table |
| 3 | Naming family (`kit-*` / `port-*`) | **Open** | [NAMING_FAMILY_DECISION_PLACEHOLDER.md](../../governance/NAMING_FAMILY_DECISION_PLACEHOLDER.md) |
| 4 | Published package aliases | **Pending** | Track per package in ADRs |
| 5 | Canonical Rust workspace | **Pending** | [rust-shared-workspace-decision.md](./rust-shared-workspace-decision.md) |
| 6–8 | Arch / schema / changelog gates | **Spec** | [architecture-and-schema-gates-spec.md](./architecture-and-schema-gates-spec.md) |
| 9–11 | Config / middleware / logging migration PRs | **Outline** | [migration-pr-plans-config-middleware-logging.md](./migration-pr-plans-config-middleware-logging.md) |
| 12 | Plugin contract template | **Done** | [plugin_contract_template.md](../../governance/plugin_contract_template.md) |
| 13 | Worktree path policy | **Done** | [worktree-path-policy.md](../../governance/worktree-path-policy.md) |
| 14 | Legacy worktree roots | **Ongoing** | Use worktree governance scripts; no mass delete |
| 15 | thegent PR681 | **Superseded** | PR #763 (test) + #766 (docs) |
| 16 | thegent PR682 | **Superseded** | Pedagogy content already on `main`; split N/A |
| 17 | AgilePlus post-172 CI | **Manual** | Verify `gh run list` when Actions available |
| 18 | bifrost-extensions Pages | **Blocked** | Billing — PR #91 merged |
| 19–20 | CI hygiene + docs placement | **Spec** | [ci-hygiene-and-docs-placement-gates.md](./ci-hygiene-and-docs-placement-gates.md) |
| 21 | Dependency graph | **Methodology + script** | [polyrepo-dependency-graph-methodology.md](./polyrepo-dependency-graph-methodology.md), [scripts/scan-phenotype-dependency-refs.sh](../../../scripts/scan-phenotype-dependency-refs.sh) |
| 22 | Release train (shared libs) | **Done** | [release-train-policy-shared-libs.md](./release-train-policy-shared-libs.md) |
| 23 | Ecosystem architecture index | **Done** | [PHENOTYPE_ECOSYSTEM_ARCHITECTURE_INDEX.md](../../reference/PHENOTYPE_ECOSYSTEM_ARCHITECTURE_INDEX.md) |
| 24 | Migration status dashboard | **Done** | [migration-status-dashboard.md](./migration-status-dashboard.md) |

## Current blockers

- **GitHub Actions billing** — CI/Pages unreliable; use local verification and `gh pr merge --admin` when policy allows.
- **Naming family** — needs explicit ADR (placeholder file above).

## Proposal link

- [proposal.md](./proposal.md)
