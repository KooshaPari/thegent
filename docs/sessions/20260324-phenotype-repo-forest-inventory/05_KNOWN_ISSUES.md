# Known Issues

## Child-agent spawn routing

- The child-agent spawn path is not honoring the requested model consistently in this session.
- Requested `gpt-5.4-mini` medium lanes were routed to a `gpt-5.3-codex-spark` backend and then hit the usage ceiling.
- This makes child-agent delegation unreliable for the current pass.

## Operational impact

- Do not treat child-agent spawn success as proof that the requested model was used.
- Use the session worklog and direct shell inventory as the source of truth until the routing issue is verified.

## Repo inventory blockers

- `heliosApp` and `heliosCLI` have pointer-style worktree changes plus branch-ahead drift that need intent confirmation before any merge or restack.
- `phenotype-config` is a live broad migration lane in the shared root checkout; the remaining
  work is migration cleanup and branch-state normalization, not stale `spec-kitty.*` inventory.
- `AgilePlus` is still carrying generated scaffolding that should be checked against the intended
  command/docs contract before merge.
- `phenodocs` now builds cleanly after local docs dependencies were installed; the tracked
  VitePress temp artifacts are restored after validation so the working copy stays usable.
- `phenodocs` local forest noise from `.agents/` and `worktrees/` is now ignored via the repo
  `.gitignore`; only real source drift remains visible.
- `trash-cli` has one untracked workflow file that needs an allow/deny decision.
- `phenotypeActions` root PR inventory dumps are now treated as local generated artifacts and
  ignored via `.gitignore`; only the ignore rule itself should remain as a tracked change.
- `thegent` root forest noise is now ignored via `.gitignore`; the active worktree root is
  `worktrees/thegent/workspace` on `refactor/perf-robustness`, which is where the actual
  `harness-native` strategy refactor and `thegent-zmx-interop` adjustment live.
- `phenotype-config` is still carrying a broad canonical-root bootstrap set and mixed migration
  churn; validation is blocked until the branch/worktree state is normalized.
- `phenodocs` validation now passes in the clean worktree lane after installing local docs
  dependencies; the remaining cleanup was a duplicate `srcDir` config entry, which is now removed.
- HeliosApp recovery now has a canonical fix on the main checkout, but the repo forest still includes stale recovery worktree lanes that can surface old failures during a broad `bun test` sweep.
- The `heliosApp` package test scripts now prune `worktrees/*`, which keeps the default validation path scoped to the active checkout instead of re-running stale nested copies.
- `AgilePlus` still has a very broad worktree delta, but its compile/test gates are green; remaining cleanup is warning-level and should be folded in before merge.
- `thegent` focused regressions around policy-federation repo-name resolution, concurrency
  compatibility, config isolation, and memory fallback are now green in the active worktree lane.
  The broader repo still contains unrelated legacy `json.dumps(...).decode()` cleanup surface
  outside the validated slice, but it is no longer blocking the targeted path.
