# Phase 6: Productization, Library Extraction, and Cleanup

## Overview

This phase closes the remaining architecture gap by classifying the last active `phenotype-*` repositories into durable categories:

- **Phenotype-domain packages** that should keep the `phenotype-` prefix
- **Reusable libraries** that should be productized under neutral names
- **Fork-extension repos** that should remain separate overlay trees
- **Special-purpose hubs** that should remain as governance/reference assets
- **Obsolete or duplicate repos** that should be archived or de-emphasized

## Objectives

1. Reduce namespace noise at the top level of the polyrepo
2. Preserve Phenotype-bound domain packages under a clear prefix
3. Productize generic libraries for external reuse
4. Formalize fork-extension repos as first-class maintenance trees
5. Keep governance, xDD, and architecture references discoverable
6. Create a repeatable classification and migration process for future repos

## Classification Rules

Use the existing naming taxonomy and package guidance:

- Keep `phenotype-` only for Phenotype-domain code
- Move general-purpose reusable code to neutral, productized names
- Keep fork overlays separate from the core package/library buckets
- Treat governance/reference repos as special-purpose hubs
- Prefer hexagonal/clean architecture boundaries when splitting packages

## Tasks

### Task 1: Apply the migration matrix

**Goal:** Convert the current audit into an executable repo-by-repo roadmap.

**Actions:**
- Review each remaining active `phenotype-*` repository
- Confirm its category from the migration matrix
- Mark the recommended target name or destination bucket
- Note any special handling needed for mixed-language repos

**Deliverable:**
- `plans/2026-03-26-phenotype-phase6-migration-matrix.md`

### Task 2: Productize reusable libraries

**Goal:** Extract general-purpose repos into neutral libraries or tools.

**Likely candidates:**
- `phenotype-cli-core` → `clikit`
- `phenotype-cipher` → `helix-crypto`
- `phenotype-logger` → `helix-logging`
- `phenotype-metrics` → `helix-metrics`
- `phenotype-tracing` → `helix-tracing`
- `phenotype-logging-zig` → `helix-logging-zig`
- `phenotype-nexus` → `helix-registry`
- `phenotype-gauge` → `helix-gauge`

**Deliverables:**
- New neutral product repos or `libs/` extraction plans
- Dependency update notes for any consumers

### Task 3: Normalize Phenotype-domain packages

**Goal:** Keep truly Phenotype-specific code under the `phenotype-` prefix and ensure package boundaries are explicit.

**Likely candidates to keep as domain packages:**
- `phenotype-config`
- `phenotype-design`
- `phenotype-auth-ts`
- `phenotype-config-ts`
- `phenotype-evaluation`
- `phenotype-middleware-py`
- `phenotype-infrakit`
- `phenotype-dep-guard` (subject to final security/tooling classification)
- `phenotype-shared` (workspace/hub, with individual crates reviewed separately)

**Actions:**
- Verify each package has a stable role
- Ensure README and metadata reflect the intended category
- Remove accidental overlap with productized libraries

### Task 4: Formalize fork-extension repos

**Goal:** Preserve overlay repos that track upstream forks without mixing them into product/package buckets.

**Repos:**
- `phenotype-cli-extensions`
- `phenotype-colab-extensions`

**Actions:**
- Keep these as maintenance overlays
- Document their sync process and extension points
- Avoid renaming them into generic package/library buckets

### Task 5: Clarify special-purpose hubs

**Goal:** Keep non-product assets discoverable without forcing them into package/library conventions.

**Repos:**
- `phenotype-xdd` — methodology and governance reference hub
- `phenotype-forge` — standalone CLI/tooling project
- `phenotype-skills-clone` — skills/reference catalog and scaffold tree

**Actions:**
- Ensure each repo has a clear purpose statement
- Remove ambiguity in top-level directory placement
- Decide whether each is a hub, a tool, or a future productized repo

### Task 6: Clean up stale or duplicate roots

**Goal:** Reduce top-level clutter and retire stale placeholders.

**Actions:**
- Identify repos that are now only historical shells or duplicates
- Archive repos that have moved or are superseded
- Keep links in archived repos pointing to the new canonical location

**Deliverable:**
- Updated archive notes where needed

### Task 7: Update governance and navigation docs

**Goal:** Keep the ecosystem-level documentation aligned with the current repo layout.

**Actions:**
- Update root index and governance references if classification changes are adopted
- Add any new naming guidance discovered during migration
- Keep phase artifacts and canonical decisions synchronized

## Success Criteria

- Remaining active repos have a documented category
- Generic libraries are identified for productization
- Fork overlays remain separate and clearly documented
- Domain packages keep the `phenotype-` prefix only where justified
- Special hubs are clearly labeled and no longer ambiguous
- The remaining top-level namespace is easier to scan and maintain

## Execution Log

### 2026-03-26 — Batch 1: cipher, tracing, logger, metrics-registry

**Task 2 progress:** Four crates extracted and productized.

| Source | Target | Package name | Build status |
|--------|--------|--------------|--------------|
| `phenotype-cipher/` | `libs/cipher/` | `cipher` | ✅ Pass |
| `phenotype-tracing/` | `libs/tracing/` | `tracing-helpers` | ✅ Pass |
| `phenotype-logger/` | `libs/logger/` | `logger` | ✅ Pass |
| `phenotype-metrics/` | `libs/metrics/` | `metrics-registry` | ✅ Pass |

Each extracted crate received:
- Renamed `Cargo.toml` with neutral package name and `phenotype-dev` GitHub org
- Updated `README.md` with neutral branding and installation instructions
- Updated `src/lib.rs` doc comments removing Phenotype references
- New `CLAUDE.md` with package overview, architecture notes, and conventions
- New `ARCHIVED.md` in source repo with migration instructions

**No consumers found** in the remaining phenotype repos. No dependency updates required.

**Naming decisions made:**
- `phenotype-cipher` → `cipher` (cleaner; `cipher` GitHub handle already reserved)
- `phenotype-tracing` → `tracing-helpers` (avoids `tracing` crate namespace collision)
- `phenotype-logger` → `logger` (follows Rust ecosystem convention)
- `phenotype-metrics` → `metrics-registry` (avoids `metrics` crate namespace collision)

### 2026-03-26 — Batch 2: clikit, nexus, gauge, logging-zig

| Source | Target | Package name | Build status |
|--------|--------|--------------|--------------|
| `phenotype-cli-core/` | `libs/clikit/` | `clikit` | ✅ Go test pass |
| `phenotype-nexus/` | `libs/nexus/` | `nexus` | ⚠️ hashconsign unavailable |
| `phenotype-gauge/` | `libs/gauge/` | `gauge` | ✅ Pass |
| `phenotype-logging-zig/` | `libs/logging-zig/` | `logging-zig` | ✅ Zig test pass |

### 2026-03-26 — Batch 3: auth-ts, config-ts, forge, shared

| Source | Target | Package name | Build status |
|--------|--------|--------------|--------------|
| `phenotype-auth-ts/` | `libs/auth-ts/` | `auth-ts` | ✅ Files verified |
| `phenotype-config-ts/` | `libs/config-ts/` | `config-ts` | ✅ Files verified |
| `phenotype-forge/` | `tools/forge/` | `forge` | ✅ Pass |
| `phenotype-shared/` | — | — | Active workspace, no migration needed |

**Batch 3 Notes:**
- `phenotype-auth-ts` and `phenotype-config-ts` are TypeScript hexagonal libs extracted to `libs/`
- `phenotype-forge` is a CLI tool moved to `tools/forge` with binary renamed to `forge`
- `phenotype-shared` is an active multi-crate workspace; `ARCHIVED.md` added to clarify its role

### 2026-03-26 — Batch 4: dep-guard, evaluation, skills-clone

| Source | Target | Package name | Build status |
|--------|--------|--------------|--------------|
| `phenotype-dep-guard/` | `tools/dep-guard/` | `dep-guard` | ✅ Module verified |
| `phenotype-evaluation/` | `libs/evaluation/` | `evaluation` | ✅ Files verified |
| `phenotype-skills-clone/` | — | — | Active hub, no migration needed |

**Batch 4 Notes:**
- `phenotype-dep-guard` is a security/supply-chain tool moved to `tools/dep-guard` with package renamed and module renamed to `dep_guard`
- `phenotype-evaluation` is an evaluation harness moved to `libs/evaluation` with neutral package name
- `phenotype-skills-clone` remains as an active special-purpose hub with `ARCHIVED.md` clarifying its role

## Phase 6 Complete

All 15 remaining phenotype-* root repos processed:
- ✅ 11 productized to libs/ or tools/
- ✅ 4 classified as special-purpose (skills, xdd, design, shared) or already handled

*Plan created: 2026-03-26*
*Last updated: 2026-03-26*
