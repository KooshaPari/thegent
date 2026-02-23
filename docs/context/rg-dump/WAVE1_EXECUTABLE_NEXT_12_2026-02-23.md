# Wave-1 execution (12 items): do-now

Date: 2026-02-23
Owner: you + 6 child agents + lead

## Current baseline snapshot
- Active branch in `thegent`: `wip/main-dirty-pre-consolidation-20260222`
- HEAD: `d3ae3a7fb`
- Remote: `origin` -> `https://github.com/KooshaPari/thegent.git`
- Stash count: none
- Main worktree is not clean (many modified and untracked files)
- Active branches and working sets are present in `.worktrees/...` and many `shadow-run_*` detached-worktree states

## 12 concrete tasks to run in this wave

1. Create a clean baseline checkpoint file: `git -C thegent status -sb`, `git -C thegent log --oneline --decorate --graph -n 20`, `git -C thegent stash list`.
2. Capture and prune stale worktree inventory for the session (`git -C thegent worktree list`, `git -C thegent worktree prune --dry-run`).
3. Re-base from `origin/main` and merge `temp/consolidate-main` and `wip/main-dirty-pre-consolidation-20260222` into a staged consolidation branch (after conflict review).
4. Move/rename any non-authoritative `main` references to `main` in local task docs.
5. Freeze all 12 items in a single wave tracker under `docs/reference` and attach this artifact link.
6. Launch 6 child agents with explicit pairs:
   - Agent-1: items 1,2
   - Agent-2: items 3,4
   - Agent-3: items 5,6
   - Agent-4: items 7,8
   - Agent-5: items 9,10
   - Agent-6: items 11,12
7. In parallel, complete `agentapi++`/`agentapi` path canonicalization across new fork boundaries and confirm only `agentapi++/` and `archive/agentapi++_legacy_2026-02-23` are used by docs/tools.
8. Validate `contracts/provider-bridge` gap coverage and finalize schema/adapter IDs for adapters.
9. Confirm `thegent` has no remaining `agentapi/` assumptions for CLI proxy orchestration that would block `agentapi++` fork wiring.
10. Apply first adapter hardening item from OpenRouter gap analysis: Authorization/header propagation and middleware-level request normalization.
11. Continue CPython 3.14 / PyPy 3.11 compatibility audit in `thegent` + `contracts/provider-bridge`.
12. Capture child-agent artifacts with exact file paths, modified sets, and merge status before touching merge/traffic decisions.

## Command pack (ready-to-run)
- `git -C thegent status -sb`
- `git -C thegent branch --all --format='%(refname:short)' | head -n 200`
- `git -C thegent stash list`
- `git -C thegent worktree list`
- `git -C thegent remote -v`

## Completion rule
No merge, delete, or cleanup action before a 6-item preflight review confirms: no untracked session artifacts are needed, and all agents have signed the 12-item assignment.
