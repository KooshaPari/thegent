# Polyrepo Productization Wave

## Intent

Drive a forward-only re-architecture of the Phenotype ecosystem toward:

- strict hexagonal boundaries,
- reusable cross-repo libraries,
- smaller autonomous services,
- plugin-ready extension contracts,
- productized public-facing packages with stable APIs.

This plan treats each repository as either:

1. `phenotype-bound` (must keep Phenotype identity), or
2. `market-neutral` (should be libified/productized for broad developer reuse).

## Why now

- Current naming and topology show duplication and mixed intent (`phenotype-*` used for both domain-bound and generic components).
- Worktree and top-level organization conventions are partially inconsistent across active repositories.
- CI and GitHub Pages quality varies across repos; a standardized architecture and release process is needed.

## Phased WBS (with DAG)

### Phase 1 - Discovery and Classification

- `P1.1` Build canonical inventory of repos, packages, crates, modules, workflows.
- `P1.2` Classify each repo/package as `phenotype-bound` or `market-neutral`.
- `P1.3` Detect duplicate capability clusters (config/auth/middleware/logging/hexagonal/tooling).
- `P1.4` Produce rename and migration map with semver impact levels.

### Phase 2 - Architecture Contracts

- `P2.1` Define shared ports and plugin contracts (input/output schemas, error model, compatibility rules).
- `P2.2` Create language-level conformance matrices (Go/TS/Python/Rust/Zig/C#).
- `P2.3` Define CI policy gates for hexagonal boundaries, schema compatibility, and quality bars.
- `P2.4` Introduce architecture test harnesses (import/layer checks, contract tests).

### Phase 3 - Libification and Productization

- `P3.1` Extract generic libs from phenotype-bound repos into neutral package families.
- `P3.2` Introduce stable versioning and changelog automation for extracted libs.
- `P3.3` Publish migration shims only where externally required; otherwise execute forward migration.
- `P3.4` Add docs/build/release templates to each productized repo.

### Phase 4 - Service and Plugin Decomposition

- `P4.1` Decompose oversized repos into domain services and shared libs using hexagonal boundaries.
- `P4.2` Add plugin registries and adapter contracts where extensibility is required.
- `P4.3` Enforce asynchronous inter-service integration defaults where feasible.
- `P4.4` Remove duplicate local implementations after shared libs are integrated.

### Phase 5 - Verification, Delivery, and Governance

- `P5.1` Run repo-by-repo CI, policy-gate, and security-gate hardening.
- `P5.2` Fix and re-run GitHub Pages deployments and docs pipelines.
- `P5.3` Complete PR/merge wave with release notes and version bumps.
- `P5.4` Publish ecosystem architecture index and maintenance checklist.

## Task Dependency DAG

- `P1.1 -> P1.2 -> P1.3 -> P1.4`
- `P1.4 -> P2.1 -> P2.2 -> P2.3 -> P2.4`
- `P2.4 -> P3.1 -> P3.2 -> P3.3 -> P3.4`
- `P3.4 -> P4.1 -> P4.2 -> P4.3 -> P4.4`
- `P4.4 -> P5.1 -> P5.2 -> P5.3 -> P5.4`

## Cross-Project Reuse Opportunities

- **Config stack**
  - Candidate: `phenotype-config`, `phenotype-config-ts`, related adapters.
  - Target shared location: neutral `config-kit` family.
  - Impacted repos: `heliosApp`, `heliosCLI`, `thegent`, `AgilePlus`, infra repos.
  - Migration order: contracts -> shared libs -> app/service integrations.

- **Hexagonal foundations**
  - Candidate: `phenotype-go-hexagonal`, `phenotype-ts-hexagonal`, `phenotype-py-hexagonal`, rust equivalents.
  - Target shared location: neutral `hex-kit` family.
  - Impacted repos: all service/template repos.
  - Migration order: architecture tests -> core libs -> templates -> apps.

- **Auth/middleware/logging**
  - Candidate: `phenotype-auth-ts`, `phenotype-go-auth`, middleware/logging packages.
  - Target shared location: neutral `auth-kit`, `middleware-kit`, `trace-kit`.
  - Impacted repos: API/microservice repos and CLIs.
  - Migration order: adapter interfaces -> package extraction -> caller migration.

- **Infrakit/shared rust capability**
  - Candidate: duplicated rust utility crates in `phenotype-infrakit`/`phenotype-shared`.
  - Target shared location: one canonical workspace with productized crates.
  - Impacted repos: rust services and tools.
  - Migration order: dedupe -> API freeze -> crate release -> downstream updates.

## Initial execution queue (next wave)

1. Complete PR + CI stabilization for `bifrost-extensions`, `AgilePlus`, `heliosApp`, `thegent` carryover branches.
2. Produce naming decision table for all `phenotype-*` repos (`keep`, `rename`, `merge`, `archive`).
3. Start first extraction batch: config + middleware neutralization candidates.
4. Apply top-level hygiene improvements and codify in governance checks.

## Decision gates requiring user confirmation

- Final neutral naming family (`forge-*`, `port-*`, `kit-*`, or another standard).
- Which currently published package names must remain for compatibility.
- Merge strategy for duplicated rust capability between `phenotype-infrakit` and `phenotype-shared`.
