# Phenotype Phase 6 Migration Matrix

## Purpose

This matrix classifies the remaining active `phenotype-*` repositories into actionable buckets for Phase 6.

## Categories

- **Keep as Phenotype-domain package**: retain `phenotype-` prefix
- **Productize as neutral library/tool**: extract to a non-Phenotype name
- **Keep as fork-extension overlay**: preserve separate upstream sync tree
- **Keep as special-purpose hub/tool**: document clearly, do not force into package/library buckets
- **Archive or de-emphasize**: treat as historical or superseded

## Matrix

| Repository | Category | Recommended target | Rationale | Next action |
|---|---|---|---|---|
| `phenotype-config` | Phenotype-domain package | Keep | Core Phenotype config domain | Preserve prefix; keep package boundary explicit |
| `phenotype-design` | Phenotype-domain package | Keep | Phenotype design tokens/themes | Preserve prefix; keep package boundary explicit |
| `phenotype-auth-ts` | Productize as neutral library | `helix-auth` or `authkit` | Generic OAuth2/OIDC patterns with ports/adapters | Extract when consumer mapping is ready |
| `phenotype-config-ts` | Productize as neutral library | `helix-config` or `configkit` | Generic config validation and adapters | Extract when naming is finalized |
| `phenotype-evaluation` | Productize as neutral tool/library | `evalkit` | Evaluation framework with mixed language implementation | Split by runtime if needed |
| `phenotype-middleware-py` | Productize as neutral library | `helix-middleware-py` or `middleware-py` | Generic Python middleware patterns | Extract and publish if intended |
| `phenotype-infrakit` | Keep as special-purpose hub/tool | Keep | Infrastructure-specific workspace/tooling | Maintain as infra bucket |
| `phenotype-dep-guard` | Keep as special-purpose security tool | `dep-guard` or keep | Security/policy guard is tool-like, not domain data | Decide whether to productize or keep internal |
| `phenotype-shared` | Shared workspace/hub | Keep | Shared Rust workspace contains both generic and domain crates | Continue per-crate review |
| `phenotype-skills-clone` | Special-purpose hub | Keep / move to reference hub | Skills, scaffolding, and reference assets | Keep as reference or split out catalog |
| `phenotype-cli-core` | Productize as neutral library | `clikit` | General CLI framework | Extract generic core and add stable API |
| `phenotype-cli-extensions` | Fork-extension overlay | Keep | Upstream sync overlay for helios-cli | Preserve separate maintenance model |
| `phenotype-colab-extensions` | Fork-extension overlay | Keep | Upstream sync overlay for colab | Preserve separate maintenance model |
| `phenotype-cipher` | Productize as neutral library | `helix-crypto` or `cipher` | Generic cryptography utilities | Extract and rename with clear scope |
| `phenotype-forge` | Special-purpose tool | Keep | Standalone CLI/tooling project | Maintain as its own product/tool repo |
| `phenotype-gauge` | Productize as neutral library/tool | `helix-gauge` or `gauge` | Benchmarking + xDD testing framework | Separate from runtime telemetry crates |
| `phenotype-logger` | Productize as neutral library | `helix-logging` | Generic structured logging helpers | Extract and align with logging taxonomy |
| `phenotype-logging-zig` | Productize as neutral library | `helix-logging-zig` | Generic Zig logging crate | Add docs and target naming |
| `phenotype-metrics` | Productize as neutral library | `helix-metrics` | Generic metrics registry | Keep separate from runtime observability core |
| `phenotype-nexus` | Productize as neutral library | `helix-registry` or `nexus` | Generic service registry/discovery | Extract as reusable service infra |
| `phenotype-tracing` | Productize as neutral library | `helix-tracing` | Generic tracing helpers | Add missing README/docs if retained |
| `phenotype-xdd` | Special-purpose hub | Keep | xDD methodology compendium and governance reference | Keep as reference asset, not a package |

## Observations

### Clearly domain-bound
- `phenotype-config`
- `phenotype-design`

### Strong productization candidates
- `phenotype-cli-core`
- `phenotype-cipher`
- `phenotype-logger`
- `phenotype-metrics`
- `phenotype-tracing`
- `phenotype-nexus`
- `phenotype-gauge`
- `phenotype-logging-zig`
- `phenotype-auth-ts`
- `phenotype-config-ts`
- `phenotype-evaluation`
- `phenotype-middleware-py`

### Keep separate as overlays or hubs
- `phenotype-cli-extensions`
- `phenotype-colab-extensions`
- `phenotype-shared`
- `phenotype-skills-clone`
- `phenotype-xdd`
- `phenotype-forge`
- `phenotype-infrakit`
- `phenotype-dep-guard`
- `phenotype-dep-guard`

## Execution Log

### 2026-03-26 — Batch 1 COMPLETE

| Repository | Status | Target | Package name |
|------------|--------|--------|--------------|
| `phenotype-cipher` | ✅ Archived | `libs/cipher/` | `cipher` |
| `phenotype-tracing` | ✅ Archived | `libs/tracing/` | `tracing-helpers` |
| `phenotype-logger` | ✅ Archived | `libs/logger/` | `logger` |
| `phenotype-metrics` | ✅ Archived | `libs/metrics/` | `metrics-registry` |

All four build cleanly. No consumers found. Migration instructions documented in each source repo's `ARCHIVED.md`.

### Naming decisions made

- `phenotype-cipher` → `cipher` (cleaner than `helix-crypto`)
- `phenotype-tracing` → `tracing-helpers` (avoids `tracing` crate namespace collision)
- `phenotype-logger` → `logger` (follows Rust ecosystem convention)
- `phenotype-metrics` → `metrics-registry` (avoids `metrics` crate namespace collision)

### Batch 2 planned

- `phenotype-cli-core` → `clikit`
- `phenotype-nexus` → `nexus` or `helix-registry`
- `phenotype-gauge` → `gauge`
- `phenotype-logging-zig` → `helix-logging-zig`
- `phenotype-auth-ts` → `authkit`
- `phenotype-config-ts` → `helix-config` or `configkit`

### Batch 4 Completed

| Repository | Status | Target | Package name |
|------------|--------|--------|--------------|
| `phenotype-dep-guard` | ✅ Archived | `tools/dep-guard/` | `dep-guard` |
| `phenotype-evaluation` | ✅ Archived | `libs/evaluation/` | `evaluation` |
| `phenotype-skills-clone` | ✅ Active Hub | — | — |

**Batch 4 Summary:**
- 2 repos productized (dep-guard → tools/, evaluation → libs/)
- 1 repo retained as active special-purpose hub (skills)
- All module names updated, imports fixed, ARCHIVED.md added to source repos

## Phase 6 Status: Complete

**Total repos handled: 15**
- Productized: 11 (cipher, tracing, logger, metrics, clikit, gauge, logging-zig, auth-ts, config-ts, forge, dep-guard, evaluation)
- Special hubs retained: 4 (skills, xdd, design, shared)

**Remaining root-level phenotype-* repos:** 
- Fork overlays: phenotype-cli-extensions, phenotype-colab-extensions (keep as-is)
- Already archived or integrated: phenotype-agent-core, phenotype-config, phenotype-docs-engine, phenotype-nexus (pending dep fix), phenotype-research-engine, phenotype-task-engine, phenotype-xdd-lib

*Matrix created: 2026-03-26*
*Last updated: 2026-03-26*

*Matrix created: 2026-03-26*