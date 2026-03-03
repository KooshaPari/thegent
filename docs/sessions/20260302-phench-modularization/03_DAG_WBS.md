# Phench Modularization and Project-Orchestration WBS

## Current Commited Work
- [done] feat(thegent): add projects modules command and manifest listing (`018c148c3`)
- [done] feat(phench): expose runtime module discovery helper (`8a0cf4bbe`)
- [done] chore(phench): sync audit metadata and module source roots (`e692ba7e5`)

## Phases

### Phase 1: Stabilize Phenotype/projects state model
- [done] Add module manifest path wiring and loader/lister flow in phench service/runtime.
- [done] Add `phench projects modules` command for list/inspect workflows.
- [done] Add a durable manifest schema version and compatibility checks for module manifests.
- [done] Add migration helper for existing module consumers (legacy path formats).

### Phase 2: Multi-repo topology and governance
- [done] Generate reusable-module and audit snapshots and extend `tach.toml` source roots.
- [todo] Build cross-repo sweep task (excluding `4sgm`, `trace`, `parpour`, `civ`) to identify additional split candidates.
- [todo] Create shared module registry with explicit ownership and refresh cadence.

### Phase 3: Worktree-first implementation model
- [done] Confirm governance commit pattern and maintain isolated branch/worktree workflow in this session.
- [todo] Move each high-risk modularization lane into dedicated worktrees (e.g., `thegent-app`, `thegent-mcp`, `thegent-control-plane`, `thegent-execution`, `thegent-governance`).
- [todo] Add lane-level blockers and handoff artifacts for resumed execution.

### Phase 4: Runtime selection and environment handling
- [done] Add guided target/repo/ref/module selection in `phench projects run`.
- [todo] Implement project selector UX for branch timelines when `--no-interactive` is enabled (fail-fast with actionable hints).
- [todo] Add persistent execution provenance snapshot (target/repo/ref/sha, manifest hash) to status output and runtime state.

### Phase 5: Repo split and moduleization
- [todo] Scaffold module directories in this repo as repo-like boundaries (`modules/thegent-app`, `modules/thegent-mcp`, `modules/thegent-control-plane`, `modules/thegent-execution`, `modules/thegent-governance`) while preserving shared contract surfaces.
- [todo] Introduce explicit import boundaries and package-level adapters for module-to-module calls.
- [todo] Run full decomposition validation (`task quality`, targeted e2e) before merge.

## DAG / Dependency Graph

1. P1.PhenoRoot [done] -> P1.ManifestSchema -> P1.MigrationHelper
2. P1.ManifestSchema -> P2.CrossRepoSweep -> P2.Registry
3. P2.CrossRepoSweep -> P3.WorktreeLanePlan -> P3.LaneArtifacts
4. P3.WorktreeLanePlan -> P4.BRanchSelectionUX -> P4.ProvenancePersist
5. P4.ProvenancePersist -> P5.ModuleSplitScaffold
6. P5.ModuleSplitScaffold -> P5.Adapters -> P5.QualityGate

## Parallel Tracks

- Workstreams can execute in parallel after P1.ManifestSchema:
- [done] `P2.CrossRepoSweep` depends on read-only repo inventory tooling.
- [done] `P4.BranchSelectionUX` depends on stable module/selection CLI APIs.
- [done] `P3.WorktreeLanePlan` depends on team/governance policy documents.
