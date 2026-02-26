# Agent-Assisted Development, Stacked PRs, and Feature Freeze Governance

## Objective
Create a stable, high-throughput delivery model for `thegent` and related repos (`cliproxy`, `heliosCLI`, etc.) where new features are completed first, then delivered in stacked, reviewable PRs without regressions.

## Evidence-backed principles
- Keep agent runs isolated by worktree/task branch to prevent file conflicts during parallel execution.
- Use staged ownership: prework → implementation slices → stacked PR graph → controlled merge/rebase.
- Prefer small, reviewable PRs over large catch-up PRs; keep stack depth shallow.
- Do not remove partial implementations; resume and complete them.
- Enforce explicit quality gates before moving from WIP to merge-ready:
  - `cargo test` / language test surface for touched crates
  - `cargo fmt` / lint where available
  - integration or smoke checks for dispatch/CLI wiring

## Agent workflow recommendations
1. Define tasks per independent slice before dispatch.
2. For each slice, assign one branch per worktree:
   - one task owner branch
   - one clear scope in the name (for example `freeze/thegent-git-contract`).
3. Keep a dependency chain for stacked PRs:
   - `PR-1` (contract/infra) → `PR-2` (feature) → `PR-3` (tests/docs)
4. Merge parents first, then rebase descendants with safe `--force-with-lease`.
5. Never run multi-agent edits in the same checkout folder.

## Stacked PR guardrails
- Parent PR must be logically testable and not only type-dead; it should pass its own scope checks.
- Child PRs should never depend on unknown state from unmerged siblings.
- If review feedback changes parent behavior, update and rebase all descendants before merge.
- Cap stack depth to avoid context drift; split if review latency exceeds stable cadence.

## Feature-freeze policy for this workspace
1. **Keep partial implementations**
   - No deletes/reverts to finish work.
   - Restore missing compatibility surfaces before adding new abstractions.
2. **Finish highest-risk blockers first**
   - Contract mismatches between crates (`thegent-git` ⇄ `thegent-hooks`) and Python/native parity.
   - Build/test quality gates (especially `go vet` style checks in Go repos).
3. **Stability first, then extension**
   - Re-enable ignored/inert tests once behavior is restored.
   - Add explicit test gating per slice, not as one global batch.

## Practical rollout order (recommended)
1. `thegent-git` contract recovery
   - Restore `status_short`, `diff_stats`, and status payloads used by hooks.
2. `thegent-hooks` changed-files hardening
   - Ensure `changed-files` uses path-aware output and handles missing binary gracefully.
3. Re-enable focused Phase 1.5 tests
4. Python parity hardening (`git_native` and parser callers)
5. cross-repo hardening for `cliproxy`/related stubs and staleness cleanup

## Immediate risk register
- API shape drift between Python and Rust entry points.
- Incomplete stacks where child PRs depend on unmerged parent assumptions.
- Ignored/inert tests masking regressions from partial implementation.
- Multi-repo tracking drift (workstream vs FR tracker divergence).

## Acceptance checklist before each merge
- `git` contract contracts unchanged (status/diff schema stable).
- PR changes are slice-complete and non-regressive.
- Evidence attached to PR:
  - files changed summary
  - targeted test/verify commands
  - open risks or follow-ups
  - parent PR dependency chain

