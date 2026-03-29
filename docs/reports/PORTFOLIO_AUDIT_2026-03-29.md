# Portfolio audit snapshot (2026-03-29)

This report captures the first execution pass for “do it all”: locate Pheno SDK, clone canonical sources, freeze a GitHub org inventory, register work in AgilePlus, and record decomposition hints against Phenotype governance.

## AgilePlus

- **Feature slug:** `portfolio-audit-kooshapari-2026`
- **App / DB:** `apps/AgilePlus` (spec and plan under `kitty-specs/portfolio-audit-kooshapari-2026/`)
- **Next CLI steps:** `agileplus research --feature portfolio-audit-kooshapari-2026 --repo <path> --mode feasibility` after refining acceptance criteria, then `agileplus plan --feature portfolio-audit-kooshapari-2026 --max-wps 20` to expand work packages beyond the default single WP.

## Pheno SDK: canonical location

| Item | Detail |
|------|--------|
| **GitHub (active)** | `KooshaPari/phenoSDK` — default branch `main`, last push **2026-02-23** |
| **GitHub (legacy name)** | `KooshaPari/pheno-sdk` — **empty repository** (clone has no commits); older description referenced ATOMS-PHENO / private package wording. A local clone attempt under `worktrees/pheno-sdk-legacy/main` is empty; that folder is gitignored—remove manually if desired. |
| **Local clone (worktree)** | `Phenotype/repos/worktrees/phenoSDK/main` — shallow clone for audit |

No separate `pheno-sdk` source tree exists under `CodeProjects`; documentation stubs live at `docs/projects/pheno-sdk/` (this repo).

## Scale and language (phenoSDK)

- **Primary language:** Python under `src/pheno/` (hexagonal-ish layout already: `domain`, `application`, `ports`, `adapters`, `infrastructure`, `infra`, `cli`, `mcp`, etc.).
- **tokei (excluding `*.json` artifacts):** on the order of **~420k lines** classified as Python code across **~2.3k** Python files (exact totals depend on markdown/code fence attribution in tokei).
- **Polyglot manifests:** no `go.mod`, `Cargo.toml`, `Package.swift`, or `build.gradle.kts` at repo root in this snapshot — treat as **Python-first**; any Go/Rust/TS/Zig productization should land in **separate Phenotype libs** with SDD contracts, not as ad-hoc folders inside this monolith.

## Decomposition crosswalk (initial)

Map `src/pheno/<area>` to existing or new **productized** packages under `Phenotype/repos` (see `docs/governance/23_ARCHITECTURAL_GOVERNANCE.md`):

| phenoSDK area | Likely extraction / alignment |
|---------------|------------------------------|
| `auth`, `credentials`, `security` | `phenotype-auth-ts`, `libs/python/phenotype-*`, shared policy packages |
| `mcp`, `clink`, `llm`, `providers` | `packages/phenotype-thegent-*`, MCP tooling, contract-first APIs |
| `cicd`, `deployment`, `kits/deploy` | `phenotype-infrakit`, `phenotype-ops`, template-program-ops |
| `observability`, `logging`, `quality` | `phenotype-logging-zig`, evaluation/metrics crates, shared QA hooks |
| `domain`, `application`, `ports`, `adapters` | Keep as **reference** for ports; migrate **interfaces** into `hexagonal-py` / `libs/hexagonal-*` patterns per language |

**PyO3 / native acceleration:** only after hot-path profiling; default is thin Rust/Zig extensions behind stable Python ports.

## KooshaPari GitHub inventory

- **249** repositories exported (name + `pushedAt` + archive/private flags).
- **Data file:** `docs/reports/data/KOOSHPARI_GITHUB_REPOS_2026-03-29.tsv`

Use this file to drive phased triage (stale vs active, duplicate `phenotype-*` vs monorepo `repos`).

## Local CodeProjects (non-exhaustive)

- **`CodeProjects/KooshaPari`:** `Dino`, `Dino-practices` (game/sim stacks).
- **`CodeProjects/archive`:** large historical trees (`Rust`, `dmouse`, `local2`, …) — audit separately using the same TSV + “last touched” rules.
- **`CodeProjects/orphans`**, **`Dev`**, **`learning`:** sample experiments; link each to a remote or mark archive-only.

## atoms.tech / capstone

Use historical atoms-era code **only** for product ideas and patterns. Do not transplant sponsor-specific artifacts verbatim; re-implement behind Phenotype contracts.

## Follow-up (execution waves)

1. Deep lint/test smoke on `worktrees/phenoSDK/main` (local only; GitHub Actions billing may block CI).
2. Expand AgilePlus plan to **20 WPs**: org clusters, Pheno SDK slice owners, CI templates, contract packages.
3. Per-repo ADRs in target libs for each extraction boundary.
