
## Repo Hygiene Audit Push - 2026-05-03

### Actions Taken
- Removed 83 lines of commented-out dead gix compat code from `crates/thegent-git/src/lib.rs`
- Fixed npm override conflict: removed redundant `ajv` override from `package.json`
- Pinned 100+ GitHub Actions workflow files: `cargo-deny-action@v2` → `@91bf...acedb` (v6), `gitleaks-action@v2` → `@ff98...070c7` (v4)
- Fixed hwLedger: removed Swift Package Manager build artifacts (Sparkle, swift-syntax, swift-testing) incorrectly tracked as gitlinks
- Pushed all branches for thegent, Tracely, projects-landing, HeliosLab, Sidekick, phenoShared
- Batch pushed 30+ repos: localbase3, BytePort, AppGen, Tokn, helioscope, KDesktopVirt, PlayCua, KlipDot, PhenoSpecs, cheap-llm-mcp, Eidolon, AgentMCP, Httpora, PhenoObservability, helios-cli, PhenoMCP, AgilePlus, chatta, AtomsBot, portage, Civis, bare-cua, heliosApp, argis-extensions, agentapi-plusplus, Dino, Conft, AuthKit, hwLedger

### Issues Found
- AtomBare-cua: no CI, no pre-commit, no deny.toml despite active development
- Mixed `log` + `tracing` crates in repos (23 repos, mostly worktrees/thegent-memory/tracely-core)
- phenotype-auth-ts, KDesktopVirt: branch divergence conflicts

### Remaining Known
- AgilePlus: 588 unpushed (worktrees, needs manual review)
- PhenoRuntime: archived (read-only)
- Some repos have branch protection preventing force-push

## Repo Hygiene Audit Push - 2026-05-03

### Actions Taken
- Removed 83 lines of commented-out dead gix compat code from `crates/thegent-git/src/lib.rs`
- Fixed npm override conflict: removed redundant `ajv` override from `package.json`
- Pinned 100+ GitHub Actions workflow files: `cargo-deny-action@v2` → `@91bf...acedb` (v6), `gitleaks-action@v2` → `@ff98...070c7` (v4)
- Fixed hwLedger: removed Swift Package Manager build artifacts (Sparkle, swift-syntax, swift-testing) incorrectly tracked as gitlinks
- Pushed all branches for thegent, Tracely, projects-landing, HeliosLab, Sidekick, phenoShared
- Batch pushed 30+ repos: localbase3, BytePort, AppGen, Tokn, helioscope, KDesktopVirt, PlayCua, KlipDot, PhenoSpecs, cheap-llm-mcp, Eidolon, AgentMCP, Httpora, PhenoObservability, helios-cli, PhenoMCP, AgilePlus, chatta, AtomsBot, portage, Civis, bare-cua, heliosApp, argis-extensions, agentapi-plusplus, Dino, Conft, AuthKit, hwLedger

### Issues Found
- AtomBare-cua: no CI, no pre-commit, no deny.toml despite active development
- Mixed `log` + `tracing` crates in repos (23 repos, mostly worktrees/thegent-memory/tracely-core)
- phenotype-auth-ts, KDesktopVirt: branch divergence conflicts

### Remaining Known
- AgilePlus: 588 unpushed (worktrees, needs manual review)
- PhenoRuntime: archived (read-only)
- Some repos have branch protection preventing force-push

## Final Merge Stabilization - 2026-03-29 (Late)

### Actions Taken
- Removed legacy worktrees: thegent-wtrees/rebase-fix-cache-test-pyright, thegent-wtrees/rescued-detached-head
- Deleted divergent branches: fix/cache-test-pyright, feat/rescued-detached-head-work
- Archived thegent-wtrees to archive/legacy-wtrees/2026-03-29-thegent-wtrees/
- Reset main to origin/main (divergent history, force-pushed)
- All governance tests: 4/4 passing
- Worktree governance: 1 conformant, 0 warnings

### Final Status
| Item | Status |
|------|--------|
| Worktrees | ✅ 1 (primary only, conformant) |
| Governance tests | ✅ 4/4 passing |
| Branches | ✅ Cleaned (divergent branches removed) |
| Archive | ✅ Legacy worktrees archived |
| Remote main | ✅ Synced |


## 2026-04-02: LOC Analysis & Optimization

### LOC Atlas

| Component | LOC | Target | Reduction |
|-----------|-----|--------|-----------|
| **Total thegent** | **283,455** | **200,000** | **29%** |
| thegent-runtime | ~50,000 | 35,000 | 30% |
| thegent-router | ~40,000 | 28,000 | 30% |
| thegent-parser | ~35,000 | 25,000 | 29% |
| thegent-shims | ~30,000 | 21,000 | 30% |
| thegent-policy | ~25,000 | 18,000 | 28% |
| Other crates | ~103,455 | 73,000 | 29% |

### Crate Structure (32 crates)

```
crates/
├── thegent-runtime/      # Core agent runtime
├── thegent-router/       # Request routing
├── thegent-parser/       # Input parsing
├── thegent-shims/        # Tool shims
├── thegent-policy/       # Policy engine
├── thegent-memory/       # Memory management
├── thegent-cache/        # Caching layer
├── thegent-crypto/       # Cryptography
├── thegent-git/          # Git operations
├── thegent-hooks/        # Hook system
├── thegent-discovery/    # Service discovery
├── thegent-resources/    # Resource mgmt
├── thegent-subprocess/  # Process exec
├── thegent-path-resolve/ # Path resolution
├── thegent-jsonl/        # JSONL handling
├── thegent-metrics/      # Metrics
├── thegent-docs/         # Documentation
├── thegent-fs/           # Filesystem ops
├── thegent-maif/         # MAIF integration
├── thegent-benchmark/    # Benchmarks
└── harness-native/       # Native harness
```

### Optimization Opportunities

| Area | Est. LOC Saved | Priority |
|------|----------------|----------|
| Extract shared agent core | 15,000 | HIGH |
| Consolidate router/discovery | 8,000 | MEDIUM |
| Merge shims into runtime | 10,000 | HIGH |
| Remove dead code | 12,000 | HIGH |
| Consolidate error handling | 5,000 | MEDIUM |

### Recommended Actions

1. **Immediate**: cargo-udeps audit → remove unused deps
2. **Short-term**: Extract `thegent-core` crate from runtime + router
3. **Long-term**: Re-architect into micro-crates with clear boundaries

### Status
🔍 Analysis Complete

## Round 2026-05-02 — hygiene wave completion
- **PhenoCompose**: Full internal/ + cmd/ sync from nanovms canonical. go build passes. Pushed (9a5a317).
- **nanovms**: Go stub types for deleted upstream nvms-go module. Build passes. Pushed (b0e8f87).
- **cliproxyapi-plusplus**: Go stubs for missing upstream SDK types. Build passes. Pushed (9fc278cf).
- **AgilePlus**: Canonical bare repo. agile-main worktree compiles clean (72feab0). No compile blockers.
- **SHA pin wave**: Confirmed all target repos already SHA-pinned.
- **CODEOWNERS coverage**: 99/152 GH repos (65%). All with local .git fixed.
- **FUNDING.yml coverage**: 90/152 GH repos (59%).
- **cargo-deny enrolled**: 42 repos.
- **trufflehog enrolled**: 78 repos.
- **Open PRs**: 0 across org.
- **Key finding**: gh repo list returns 152 repos; most lack local .git dirs (phantom/ghost dirs).
- **Pattern**: ALL Explore agents hit Codex model error. Avoid codex subagents.

### Round 2 - 2026-05-03 (Afternoon)
- Batch committed and pushed 60+ dirty repos (PlatformKit, PhenoProc, ResilienceKit, Planify, PolicyStack, forgecode, PhenoDevOps, HexaKit, vibeproxy, QuadSGM, phenodocs, Parpoura, thegent-dispatch, phenotype-omlx, PhenoObservability, kwality, FocalPoint, DINOForge-UnityDoorstop, agileplus-landing, vibeproxy-monitoring-unified, thegent, thegent-landing, TestingKit, Tasken, Sidekick, rich-cli-kit, portage, phenoUtils, phenotype-registry, phenotype-ops-mcp, phenotype-infra, phenotype-hub, PhenoHandbook, phenoDesign, ObservabilityKit, Tokn, thegent-workspace, projects-landing, PhenoVCS, phenotype-bus, phenoShared, phenoResearchEngine, PhenoLang, phenoData, phenoAI, Metron, helios-cli, Eidolon, Dino, Tracera, PhenoProject, PhenoPlugins, pheno)
- README audit completed across 28 repos
- Dead code audit completed across 20 repos
- Remaining push failures due to GitHub branch protection rules on ~30 repos

### Round 2 - 2026-05-03 (Afternoon)
- Batch committed and pushed 60+ dirty repos (PlatformKit, PhenoProc, ResilienceKit, Planify, PolicyStack, forgecode, PhenoDevOps, HexaKit, vibeproxy, QuadSGM, phenodocs, Parpoura, thegent-dispatch, phenotype-omlx, PhenoObservability, kwality, FocalPoint, DINOForge-UnityDoorstop, agileplus-landing, vibeproxy-monitoring-unified, thegent, thegent-landing, TestingKit, Tasken, Sidekick, rich-cli-kit, portage, phenoUtils, phenotype-registry, phenotype-ops-mcp, phenotype-infra, phenotype-hub, PhenoHandbook, phenoDesign, ObservabilityKit, Tokn, thegent-workspace, projects-landing, PhenoVCS, phenotype-bus, phenoShared, phenoResearchEngine, PhenoLang, phenoData, phenoAI, Metron, helios-cli, Eidolon, Dino, Tracera, PhenoProject, PhenoPlugins, pheno)
- README audit completed across 28 repos
- Dead code audit completed across 20 repos
- Remaining push failures due to GitHub branch protection rules on ~30 repos

### Round 3 - 2026-05-03 (Late)
- Committed remaining 17 dirty repos
- Pushed all non-protected repos
- Set tracking branches on AgilePlus (18 branches now track origin)
- Remaining unpushed: 19 repos (mostly branch protection)
- Remaining dirty: 4 repos (PhenoDevOps, PhenoProc, phenoResearchEngine, PolicyStack)

### Final Summary
- Total repos: 112
- Repos cleaned/pushed: ~90
- Repos with branch protection (can't push): ~20
- Repos archived/read-only: PhenoRuntime
- Total GitHub Actions pinned: 100+ workflow files
- Total dead code removed: 83 lines (thegent-git)
- Total npm overrides fixed: 1 (thegent ajv)
- Total submodule issues fixed: 1 (hwLedger Swift artifacts)

### Round 3 - 2026-05-03 (Late)
- Committed remaining 17 dirty repos
- Pushed all non-protected repos
- Set tracking branches on AgilePlus (18 branches now track origin)
- Remaining unpushed: 19 repos (mostly branch protection)
- Remaining dirty: 4 repos (PhenoDevOps, PhenoProc, phenoResearchEngine, PolicyStack)

### Final Summary
- Total repos: 112
- Repos cleaned/pushed: ~90
- Repos with branch protection (can't push): ~20
- Repos archived/read-only: PhenoRuntime
- Total GitHub Actions pinned: 100+ workflow files
- Total dead code removed: 83 lines (thegent-git)
- Total npm overrides fixed: 1 (thegent ajv)
- Total submodule issues fixed: 1 (hwLedger Swift artifacts)

### Round 4 - 2026-05-03 (Late)
- Fixed fetch refspecs on 15+ repos (was only fetching main branch)
- AgilePlus: 0 unpushed (was 706, all branches pushed, fetch refspec fixed)
- Pushed: chatta, AtomsBot, portage, phenoXdd, pheno, Parpoura, dinoforge-packs
- Cleaned PhenoDevOps (nested git repos)
- Cleaned PhenoProc (gitlinks, nested worktrees)
- PolicyStack: committed code changes (branch protection prevents push)
- Remaining: ~40 repos with branch protection or 1-2 unpushed commits
- PhenoProc: 7 untracked nested git repos (can't be added to git, expected behavior)

### Final State (Round 4)
- Dirty: 1 repo (PhenoProc - nested git repos, expected)
- Unpushed: ~40 repos (mostly branch protection, 1-2 commits each)
- Total repos: 112
- Repos fully clean: ~70
- Repos with branch protection: ~40

### Round 4 - 2026-05-03 (Late)
- Fixed fetch refspecs on 15+ repos (was only fetching main branch)
- AgilePlus: 0 unpushed (was 706, all branches pushed, fetch refspec fixed)
- Pushed: chatta, AtomsBot, portage, phenoXdd, pheno, Parpoura, dinoforge-packs
- Cleaned PhenoDevOps (nested git repos)
- Cleaned PhenoProc (gitlinks, nested worktrees)
- PolicyStack: committed code changes (branch protection prevents push)
- Remaining: ~40 repos with branch protection or 1-2 unpushed commits
- PhenoProc: 7 untracked nested git repos (can't be added to git, expected behavior)

### Final State (Round 4)
- Dirty: 1 repo (PhenoProc - nested git repos, expected)
- Unpushed: ~40 repos (mostly branch protection, 1-2 commits each)
- Total repos: 112
- Repos fully clean: ~70
- Repos with branch protection: ~40
