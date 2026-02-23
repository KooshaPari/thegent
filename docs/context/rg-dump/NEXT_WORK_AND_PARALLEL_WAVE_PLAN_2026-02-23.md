# Next Work + Parallel Wave Plan (2026-02-23)

Scope: Continue from pending `cli proxy` + worktree consolidation intent using a 6-agent lane model and a concrete 12-item queue.

## Baseline snapshot (read-only state)
- Current primary tree: `thegent/` on branch `wip/main-dirty-pre-consolidation-20260222`.
- Branch/state status in `thegent/`: dirty with tracked and untracked changes.
- `thegent` contains many existing worktrees and detached HEAD worktrees (shadow/tracks), including:
  - `.worktrees/track1-cliproxy`
  - `.worktrees/track2-rust`
  - `.worktrees/track3-zig-quality`
  - `.worktrees/track4-split`
  - `.worktrees/tray-app`
- Stash inventory was requested but not executed in this pass.

## Wave-1 execution list (12 items)

1. Consolidation checkpoint: capture exact `git status`, `git branch`, `git stash list`, and `git worktree list` for `thegent` and save to trace.
2. Merge/close open `wip/*` and detached-head worktrees only after baseline review and conflict evaluation.
3. Normalize branch naming convention (`main` -> `main`) in active planning artifacts and runbook references.
4. Establish worktree-only branching policy for this round and block direct feature branching in main worktree.
5. Fork/align `agentapi++` legacy status so all teams consume `agentapi++` from new clone, not `archive/agentapi++_legacy_2026-02-23`.
6. Publish/refresh `provider-bridge` adapter contract: finalize `schema`, `interfaces`, `stubs`, and middleware contract baseline.
7. Implement or finalize `AgentApiMetaProviderAdapter` integration boundary in `thegent`.
8. Implement or finalize `CliproxyMetaProviderAdapter` integration boundary in `cliproxyapi-plusplus`.
9. Capture top 3 unresolved CLI proxy/API bug classes from the 2000-item execution board into concrete owner-specific fix tickets.
10. Start OpenRouter/authorization hardening pass from the web audit findings (auth header and WS forwarding checks).
11. Continue CPython 3.14 + PyPy 3.11 runtime hardening from `CPY14_PYPY311_*` artifacts.
12. Run a parallel child-agent synthesis on requested Reddit + DDG research threads and store evidence-backed workflow learnings.

## Assignment model
- Use 6 child agents + 1 lead.
- Assign 2 items per child agent now, then rotate if any item exceeds its estimate.
- Each item requires: touched paths, decision rationale, and next 1-step action.

## Suggested assignment
- Agent-1: Items 1, 2
- Agent-2: Items 3, 4
- Agent-3: Items 5, 10
- Agent-4: Items 6, 7
- Agent-5: Items 8, 9
- Agent-6: Items 11, 12
- Lead: item 1 evidence verification, conflict arbitration, and consolidation command sequencing

