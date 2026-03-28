# heliosApp / heliosApp-colab Consolidation Plan

**Status:** RESEARCH COMPLETE — awaiting implementation approval
**Date:** 2026-03-27
**Scope:** Runtime-core extraction and repo relationship clarification

---

## Executive Summary

`heliosApp` and `heliosApp-colab` are **not independent products** — they are two local checkouts of the same GitHub repository (`KooshaPari/heliosApp`). Both push to `origin git@github.com:KooshaPari/heliosApp.git`. `heliosApp-colab` also tracks an upstream at `https://github.com/blackboardsh/colab.git`, making it a **fork-with-upstream** workspace that rebases the Blackboard `colab` runtime into the heliosApp shell.

This changes the consolidation recommendation: rather than extracting a shared package between two sibling repos, the correct strategy is to **merge the colab divergence cleanly into heliosApp's main branch** and treat the colab-specific features as a named variant or feature flag set. The `@phenotype/helios-runtime-core` extraction is still valid and worthwhile for reducing future drift, but it is secondary to the merge.

---

## Key Finding: Repo Relationship

| Attribute | heliosApp | heliosApp-colab |
|---|---|---|
| GitHub origin | `KooshaPari/heliosApp` | `KooshaPari/heliosApp` |
| Upstream | `KooshaPari/heliosApp` | `blackboardsh/colab` |
| Version | `0.1.2` | `0.1.0` |
| Biome version | `2.4.9` | `1.9.4` |
| TypeScript version | `6.0.2` | `5.8.2` |
| xterm version | `^6.0.0` | `^5.5.0` |
| Extra apps | none | `apps/renderer` (SolidJS UI, 1,270 LOC) |
| Extra packages | `phenotype-metrics`, `phenotype-project` | none |
| Extra tooling | `.vitepress`, CODEOWNERS | `.kittify` missions, `turbo.json` |

`heliosApp` is the canonical, forward-moving fork. `heliosApp-colab` is a behind-version snapshot that periodically rebases from `blackboardsh/colab` upstream. The local-disk difference is a diverged working tree, not two separate products.

---

## Phase 1: Identical Files — Extractable to Shared Core

### Verdict: 247 of 259 runtime/src files are byte-for-byte identical (95.4%)

Total runtime/src LOC in heliosApp: **45,963 lines across 259 files**

The following subsystems are 100% identical between both repos and are safe to extract to `@phenotype/helios-runtime-core` without any parameterization:

| Subsystem | Files | LOC | Notes |
|---|---|---|---|
| `audit` (partial) | 14 of 17 | ~2,600 | 3 files differ — see below |
| `config` | 6 | 590 | Fully identical |
| `diagnostics` | 7 | 907 | Fully identical |
| `integrations` | 47 | 5,472 | Fully identical including all zellij, tmate, upterm, zmx, par, mcp, a2a, acp, sharing, inference |
| `lanes` (partial) | 14 of 15 | ~2,940 | 1 file differs — see below |
| `policy` | 5 | 742 | Fully identical |
| `protocol` (partial) | 17 of 19 | ~3,150 | 2 files differ — see below |
| `providers` | 23 | 6,476 | Fully identical |
| `pty` | 17 | 3,187 | Fully identical |
| `recovery` | 20 | 3,677 | Fully identical |
| `registry` | 7 | 1,045 | Fully identical |
| `renderer` | 38 | 7,006 | Fully identical |
| `secrets` | 19 | 4,161 | Fully identical |
| `sessions` (partial) | 5 of 6 | ~900 | 1 file differs — see below |
| `types` | 3 | 60 | Fully identical |
| `workspace` | 5 | 763 | Fully identical |

**Extractable LOC estimate: ~41,969 (247 files, ~91% of runtime/src)**

The `packages/errors`, `packages/ids`, and `packages/types` workspace packages are also byte-for-byte identical between both repos.

---

## Phase 2: Differing Files — Must Be Parameterized or Kept Per-Variant

### 12 files differ between the two runtime/src trees

All 12 differences represent **heliosApp advancing ahead of heliosApp-colab**, not feature divergence. The colab side is uniformly older/simpler; heliosApp adds:

| File | Nature of heliosApp Addition |
|---|---|
| `audit/in-memory-audit-sink.ts` | Stricter type casting (`as Record<string,unknown>` guards) |
| `audit/sink.ts` | Persistence chain refactor: chained `Promise<void>` replaces `boolean` flag; eviction handling for already-persisted events |
| `audit/sqlite-store.ts` | Additional PRAGMAs (`page_size`, `temp_store`, `auto_vacuum`); `INSERT OR IGNORE` instead of `INSERT`; schema failure recovery with SQLITE_IOERR_SHORT_READ handler |
| `index.ts` | Adds `InMemorySessionRegistry`, `TerminalRegistry`, `LaneLifecycleService`, `TerminalBuffer` context, `harnessProbe` option, `terminalBufferCapBytes` option, envelope passthrough |
| `lanes/index.ts` | Adds `lane.create.started` event type; emits that event on lane creation; adds `correlation_id` to lane events |
| `protocol/bus/emitter.ts` | Auto-assigns sequence numbers to unsequenced events |
| `protocol/bus/request-handlers.ts` | Enforces `terminal_id` on terminal lifecycle commands; uses `String()` coercion for id normalization |
| `runtime/fetch.ts` | Emits `session.created` event after session start; appends to audit trail |
| `runtime/ops.ts` | Exports `RuntimeOpsContext` type as public (was module-private); passes `envelope` to bus commands |
| `runtime/terminal.ts` | Adds `TerminalRegistry` to context; expands terminal state to include `"idle"` state; enriches throttle/unthrottle events with workspace/lane/session context from registry |
| `runtime/types.ts` | Adds `LocalBusEnvelope` import, `harnessProbe`, `terminalBufferCapBytes` to `RuntimeOptions`; renames `RuntimeStateSnapshot` → `RuntimeBootstrapSnapshot` with full recovery interface |
| `sessions/registry.ts` | `| undefined` explicit union type on optional fields (stylistic, TypeScript strictness) |

**Classification:** All 12 differences are **heliosApp regressions on the colab side** (colab is behind). None represent colab-specific features that need preservation. The correct fix is to advance colab to match heliosApp, not to parameterize.

### Desktop app diffs (2 files)

| File | Nature of Difference |
|---|---|
| `apps/desktop/src/settings/switch_confirmation.ts` | Tab-key focus logic: heliosApp has an `else if` chain; colab has a nested `else { if }` — functionally equivalent but structurally different |
| `apps/desktop/src/settings/switch_status.ts` | heliosApp has `biome-ignore` suppression for complexity, uses early-return guards; colab uses inline ternary string concat — functionally equivalent |

These are **style-level divergences** introduced by the colab rebase. Both are resolvable by taking heliosApp's version.

---

## Phase 3: colab-Only Content

### `apps/renderer` (1,270 LOC — only in heliosApp-colab)

A SolidJS UI layer (`App.tsx`, `ChatPanel`, `ChatInput`, `MessageBubble`, `ToolCallBlock`, `ToolResultBlock`, `Sidebar`, `TerminalPanel`, `TerminalTabs`, `StatusBar`, stores for `app`, `chat`, `terminal`).

This is the Blackboard colab upstream's renderer — a SolidJS chat+terminal interface from `blackboardsh/colab`. It does **not exist in heliosApp** and represents the primary value add from the colab fork. This must be **preserved and merged into heliosApp** as a first-class app, or kept as a separate `apps/colab-renderer` package within the monorepo.

### colab-only packages/tooling

- `.kittify/` missions and scripts (agent orchestration workflows)
- `turbo.json` (Turborepo build pipeline — heliosApp uses plain bun scripts)
- `docs/guide/` (additional guides not in heliosApp)
- `packages/` is a strict subset (missing `phenotype-metrics`, `phenotype-project`)

---

## Primary Recommendation: Merge, Not Extract

Given that both repos push to the same GitHub origin, the correct long-term move is:

**Merge `apps/renderer` from heliosApp-colab into heliosApp as a new workspace app, advance all diverged files to match heliosApp, and retire heliosApp-colab as a separate local checkout.**

The `@phenotype/helios-runtime-core` extraction is a good *second step* once the single-repo baseline is clean.

### Why merge wins over shared package

1. Both repos are already one GitHub repo — maintaining two diverging local workspaces is unnecessary operational cost.
2. The 12 differing runtime files represent heliosApp advancing forward; there is no feature split, only version lag.
3. The colab renderer is a net-new app that belongs in the heliosApp monorepo's `apps/` workspace.
4. The extracted shared package approach only makes sense if two genuinely separate products need to consume the same core — that is not the case here.

---

## Secondary Recommendation: `@phenotype/helios-runtime-core` Package

Once the repos are merged, the 247 identical runtime files should be extracted to a proper workspace package to prevent future drift.

### Proposed package location

```
/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp/packages/runtime-core/
```

### Package name

```
@helios/runtime-core
```

(following the existing `@helios/errors`, `@helios/ids`, `@helios/types` naming convention already present in both repos)

### Package structure

```
packages/runtime-core/
  src/
    audit/          (14 files — 3 remain in app layer for override)
    config/         (6 files)
    diagnostics/    (7 files)
    integrations/   (47 files)
    lanes/          (14 files — 1 remains in app layer)
    policy/         (5 files)
    protocol/       (17 files — 2 remain in app layer)
    providers/      (23 files)
    pty/            (17 files)
    recovery/       (20 files)
    registry/       (7 files)
    renderer/       (38 files)
    secrets/        (19 files)
    sessions/       (5 files — 1 remains in app layer)
    types/          (3 files)
    workspace/      (5 files)
    index.ts        (re-exports all subsystems)
  package.json      (name: @helios/runtime-core, private: true)
  tsconfig.json     (extends ../../tsconfig.base.json)
```

Files that remain in `apps/runtime/src/` (app-layer overrides):
- `runtime/fetch.ts`, `runtime/ops.ts`, `runtime/terminal.ts`, `runtime/types.ts` (4 files — tightly coupled to app bootstrap context)
- `index.ts` (entry point — assembles all subsystems, must stay in app layer)
- `audit/in-memory-audit-sink.ts`, `audit/sink.ts`, `audit/sqlite-store.ts` (3 files — storage-layer configs vary by variant)
- `lanes/index.ts` (1 file — event topology slightly variant)
- `protocol/bus/emitter.ts`, `protocol/bus/request-handlers.ts` (2 files — protocol versioning differs)
- `sessions/registry.ts` (1 file — type strictness varies by TypeScript target version)

### Workspace registration

Add to `heliosApp/package.json` workspaces:

```json
"workspaces": [
  "apps/runtime",
  "apps/desktop",
  "apps/colab-renderer",
  "packages/runtime-core",
  "packages/errors",
  "packages/ids",
  "packages/types"
]
```

---

## Migration Steps (DAG)

```
P1.1  Audit 12 differing files → confirm heliosApp version is correct in all cases
P1.2  Copy apps/renderer from heliosApp-colab → heliosApp/apps/colab-renderer
P1.3  Add colab-renderer to heliosApp workspace, verify bun install resolves

P2.1  [depends: P1.3] Create packages/runtime-core with package.json and tsconfig.json
P2.2  [depends: P2.1] Move 247 identical source files to packages/runtime-core/src/
P2.3  [depends: P2.2] Update import paths in apps/runtime/src/ to reference @helios/runtime-core
P2.4  [depends: P2.3] Run bun typecheck && bun test to verify no breakage
P2.5  [depends: P2.4] Update apps/runtime/package.json to add @helios/runtime-core dependency

P3.1  [depends: P1.3, P2.5] Open PR: "feat(monorepo): add colab-renderer + extract runtime-core"
P3.2  [depends: P3.1] Delete heliosApp-colab local checkout after PR merges
```

**Estimated agent effort:** 8-15 tool calls, 1 parallel subagent for file moves, ~5 min wall-clock.

---

## LOC Savings Estimate

| Metric | Value |
|---|---|
| Total runtime/src LOC (per repo) | 45,963 |
| Extractable to shared package | ~41,969 (247 files) |
| LOC eliminated from duplication | ~41,969 (colab checkout retired) |
| Net duplication before consolidation | ~91,926 LOC (two copies of same runtime) |
| Net duplication after consolidation | 0 (single monorepo, single runtime-core package) |
| LOC savings % | ~91% of runtime eliminated from duplication |
| App-layer residual per variant | ~3,994 LOC (12 differing files + index + bootstrap) |

---

## Files Referenced in This Plan

- heliosApp runtime/src: `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp/apps/runtime/src/`
- heliosApp-colab runtime/src: `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp-colab/apps/runtime/src/`
- heliosApp packages: `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp/packages/`
- heliosApp root package.json: `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp/package.json`
- colab renderer (to be migrated): `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp-colab/apps/renderer/`
- Proposed extraction target: `/Users/kooshapari/CodeProjects/Phenotype/repos/apps/heliosApp/packages/runtime-core/`
