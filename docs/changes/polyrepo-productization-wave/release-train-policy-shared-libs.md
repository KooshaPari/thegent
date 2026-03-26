# Release train policy — shared libraries (extracted kits)

**Scope:** Neutral and `phenotype-*` **libraries** extracted for reuse across services (Go modules, npm crates, PyPI, Cargo workspaces).

## Principles

1. **Semantic versioning** on every publish; **CHANGELOG** entry required.
2. **One release train per month** (calendar) for **patch** cadence; **minor** when API additions are backward-compatible; **major** only with migration doc.
3. **Compatibility:** consumers pin ranges in lockfiles; breaking releases get a **6-week** deprecation window for `stable` APIs when possible.

## Train schedule (default)

| Week | Action |
|------|--------|
| W1 | Cut `release/*` from `main`; integration tests on all known consumers (smoke). |
| W2 | Stabilize; docs + version bump. |
| W3 | Publish to registries; announce in ecosystem index. |
| W4 | Consumer bumps (optional batch PRs). |

Adjust per repo; link from each lib’s `README.md`.

## Multi-repo coordination

- **Dependency graph:** maintain `docs/changes/polyrepo-productization-wave/polyrepo-dependency-graph-methodology.md`.
- **Stacked PRs:** consumer updates **after** library release is tagged.

## Relation to `release-branch-governance.md`

- **Repo-level** release branches: see `docs/governance/release-branch-governance.md`.
- This document adds **cross-repo lib** coordination only.
