# Phase 1 Repo Boundary Checklists (2026-02-28)

## 1) /Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi-plusplus
- [ ] Create `internal/domain`, `internal/application`, `internal/ports`, `internal/adapters` package map document.
- [ ] Move executor logic from `internal/runtime/executor/kiro_executor.go` behind application use-cases.
- [ ] Ensure HTTP handlers in `internal/api/handlers/*` depend on application interfaces only.
- [ ] Enforce import guard: forbid adapter->adapter and cmd->domain concrete imports.

## 2) /Users/kooshapari/CodeProjects/Phenotype/repos/agentapi-plusplus
- [ ] Split transport logic from `lib/httpapi/server.go` into adapter + application orchestration.
- [ ] Define explicit routing/application contracts between `internal/routing` and `lib/httpapi`.
- [ ] Keep `cmd/server` as composition root only.

## 3) /Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI
- [ ] Decompose oversized `codex-rs/core/src/codex.rs` into domain/application modules.
- [ ] Decompose oversized `codex-rs/tui/src/bottom_pane/chat_composer.rs` into UI state + controller layers.
- [ ] Add crate-level visibility constraints to prevent cross-module reach-through.
- [ ] Keep `/sdk/typescript/src` bound to public contracts only.

## 4) /Users/kooshapari/CodeProjects/Phenotype/repos/thegent
- [ ] Declare architecture split: runtime engine (`src/thegent`) vs tooling engines (`src/docs_engine`, `src/research_engine`).
- [ ] Prevent runtime adapters from importing documentation/research internals.
- [ ] Extract shared task engine from `.kittify/scripts/tasks/` into `/Users/kooshapari/CodeProjects/Phenotype/repos/sdk/spec-kitty-task-engine`.

## 5) /Users/kooshapari/CodeProjects/Phenotype/repos/portage
- [ ] Separate CLI orchestration from adapter details in `src/harbor/cli/*`.
- [ ] Enforce dependency inversion for adapters under `adapters/` and `src/harbor/*`.
- [ ] Split large modules (`terminus_2.py`, `viewer/server.py`) by use-case boundaries.

## 6) /Users/kooshapari/CodeProjects/Phenotype/repos/tokenledger
- [ ] Split `src/ingest/mod.rs` into ingest stages with explicit traits.
- [ ] Keep `src/routing` as transport adapter; prohibit business rules there.
- [ ] Isolate `src/models.rs` domain entities from persistence/transport concerns.

## Compatibility / Mirror Repos
### /Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi++
- [ ] Freeze new feature development.
- [ ] Allow only compatibility fixes and merge-forward from `/Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi-plusplus`.

### /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli
- [ ] Freeze core runtime edits unless explicitly approved migration lane.
- [ ] Prefer wrapper/distribution concerns and consume outputs from `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI`.
