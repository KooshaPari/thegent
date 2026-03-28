# Inventory: `phenotype-*` repositories (tier & migration)

> **Purpose**: Classify every **`phenotype-*`** repo under `Phenotype/repos/` against **`PACKAGE_REPO_NAMING_TAXONOMY.md`**.  
> **Scope**: **29** directories enumerated **2026-03-25** (`ls -1d phenotype-*/`).  
> **Status**: Living document — refresh when clones are added or removed.

---

## Summary

| Classification | Count | Meaning |
|----------------|-------|---------|
| **Tier A** (keep prefix) | 12 | Org-bound policy, surfaces, engines, integrated org stacks |
| **Tier A-satellite** | 2 | Satellites of org config/auth ports (`config-ts`, `auth-ts`) |
| **Tier B** (migrate / neutral name) | 15 | Generic kits, infra, marketable libraries |
| **Triage** | 0 | — |

---

## Legend

| Column | Meaning |
|--------|---------|
| **Tier** | Target per `PACKAGE_REPO_NAMING_TAXONOMY.md` |
| **Suggested neutral name** | Illustrative rename for Tier B (ADR required) |
| **Action** | `keep` · `rename-repo` · `extract-crates` · `fix-readme` · `triage` |

---

## Full table (alphabetical)

| Repository | Purpose | Tier | Suggested neutral (B only) | Action | Notes |
|------------|---------|------|----------------------------|--------|-------|
| `phenotype-agent-core` | Agent core library | **A** | — | keep | |
| `phenotype-auth-ts` | OAuth2/OIDC TS patterns (hexagonal) | **A-satellite** | — | keep | Ports + adapters + **Vitest** green; `PlaceholderJwtVerifier` for wiring only |
| `phenotype-cipher` | Rust crypto (AES-GCM, hashing, signatures) | **B** | `cipher-rs` | rename-repo | Generic README / crate naming |
| `phenotype-cli-core` | Go CLI framework | **B** | `go-cli-core` | rename-repo | |
| `phenotype-cli-extensions` | Helios-cli fork extensions (specs, MCP, SDK) | **A** | — | keep | **README** added; see `FORK_MAINTENANCE.md` |
| `phenotype-colab-extensions` | Colab fork extensions + specs | **A** | — | keep | **README** added |
| `phenotype-config` | Org config hub (Rust primary) | **A** | — | keep | Reference Tier A |
| `phenotype-config-ts` | `@phenotype/config-ts`, Zod + file/env adapters | **A-satellite** | — | keep | **README** added |
| `phenotype-design` | Design tokens / VitePress | **A** | — | keep | |
| `phenotype-docs-engine` | Doc generation engine | **A** | — | keep | |
| `phenotype-evaluation` | Evaluation framework | **A** | — | keep | |
| `phenotype-forge` | CLI task runner (generic `forge` README) | **B** | `forge-runner` | rename-repo | |
| `phenotype-gauge` | Benchmarking + xDD testing (Rust) | **B** | `gauge-bench` | rename-repo | |
| `phenotype-go-kit` | Go infra toolkit | **B** | `go-infra-kit` | rename-repo | |
| `phenotype-infrakit` | Event sourcing, cache, policy, FSM crates | **B** | `infrakit-rs` | extract-crates | |
| `phenotype-logger` | Rust structured logging helpers | **B** | `phenotype-logger` → neutral | rename-repo | **`Cargo.toml` + tests** |
| `phenotype-logging-zig` | Zig structured logging | **B** | `zig-logging-kit` | rename-repo | **Zig 0.15**-compatible; tests green |
| `phenotype-metrics` | Rust metrics registry + Prometheus text | **B** | neutral crate | rename-repo | **`Cargo.toml` + tests** |
| `phenotype-middleware-py` | Hexagonal middleware (Python) | **B** | `py-http-middleware-kit` | rename-repo | **README** added |
| `phenotype-nexus` | Service registry / discovery | **B** | `svc-nexus` | rename-repo | |
| `phenotype-patch` | Unified diff/patch library | **B** | `patch-rs` | rename-repo | |
| `phenotype-research-engine` | Research engine | **A** | — | keep | |
| `phenotype-sentinel` | Rate limit, circuit breaker, bulkhead | **B** | `resilience-sentinel-rs` | rename-repo | |
| `phenotype-shared` | Integrated Rust hex workspace | **A** | — | keep | README corrected earlier |
| `phenotype-skills-clone` | Skills + hexagonal + crates + governance docs | **A** | — | keep | **Root README** added |
| `phenotype-task-engine` | Task orchestration | **A** | — | keep | |
| `phenotype-vessel` | Container utilities | **B** | `container-vessel-rs` | rename-repo | |
| `phenotype-xdd` | xDD compendium (docs) | **A** | — | keep | |
| `phenotype-xdd-lib` | Rust xDD test/spec utilities | **B** | `xdd-utils-rs` | rename-repo | |

---

## Wave 0 (completed in hub docs pass)

- Root **README** for repos that lacked it (see “Notes”).
- **`phenotype-logger` / `phenotype-metrics`**: `Cargo.toml`, `cargo test` green.
- **`phenotype-logging-zig`**: module doc order, Zig keyword `error` → `err`, JSON `format`, `Managed` buffers — `zig test` / **`zig build test`** green on Zig **0.15.x**; `build.zig` + `.gitignore` for `zig-out`/`.zig-cache`.

## Later waves (ADR-backed; no GitHub renames in this pass)

See **`docs/changes/phenotype-prefix-migration/`** (`proposal.md`, `tasks.md`, `GITHUB_RENAME_RUNBOOK.md`, `adr-001-hex-kits.md`, `adr-002-infra-and-generic-crates.md`).

---

## Cross-references

- `docs/engineering/PACKAGE_REPO_NAMING_TAXONOMY.md`
- `docs/changes/phenotype-prefix-migration/proposal.md`

---

*Tier suggestions are recommendations for ADRs; owners may override with rationale.*
