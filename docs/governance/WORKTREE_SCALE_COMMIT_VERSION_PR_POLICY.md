# Worktree, Commit, Version, and PR Governance Policy

## Purpose

Define a single policy model for how work is placed, committed, versioned, and merged in multi-agent execution.

## Core Rules

1. Keep the primary checkout pinned to `main`.
2. Do not run feature branch development from the primary checkout.
3. Use policy-driven worktree placement, not `1 agent = 1 worktree`.
4. Use integration worktrees to merge/cherry-pick back to `main`.

## Enforced Worktree Layout

1. Non-primary worktrees must live under `${THGENT_WORKTREE_ROOT:-<repo>/.worktrees}`.
2. Non-primary worktree paths must match `<domain>/<scale>/<change-anchor>/<state>/`.
3. Create worktrees via `./scripts/worktree_governance.sh new <domain> <scale> <change-anchor> [start-point]`.
4. Manage lifecycle state via `./scripts/worktree_governance.sh state <change-anchor> <new-state>`.
5. Validate layout via `./scripts/worktree_governance.sh check`.
6. List or prune worktrees via `./scripts/worktree_governance.sh list` and `./scripts/worktree_governance.sh prune [--dry-run]`.
7. Legacy worktrees are blocked by default. Temporary migration override:
   `THGENT_WORKTREE_ALLOW_LEGACY=1`.

## Task Scale Taxonomy

1. `XS`: single-file, low-risk, narrow change.
2. `S`: small multi-file, bounded behavior change.
3. `M`: cross-module feature/fix.
4. `L`: cross-domain refactor or protocol/interface shift.
5. `XL`: program-level change spanning lanes/phases.

## Worktree Allocation Matrix

1. `XS`: shared lane worktree.
2. `S`: shared lane worktree unless overlap-risk is high.
3. `M`: lane-dedicated worktree, with burst worktree on contention.
4. `L`: dedicated integration worktree plus optional burst worktrees.
5. `XL`: program integration worktree plus multiple lane worktrees and merge train.

## Commit Strategy Matrix

1. `XS`: one commit (two maximum).
2. `S`: micro-commits by concern (`logic`, `tests`, `docs`).
3. `M`: micro-commit chain with topic boundaries.
4. `L`: commit packages (`pkg`) per subsystem, then integration commit.
5. `XL`: phased commit packages, stabilization commits, release tags.

## Micro-Versioning Policy

1. Lane build marker: `lane.<id>.<seq>`.
2. Package marker: `pkg.<domain>.<seq>`.
3. Integration marker: `int.<wave>.<seq>`.
4. Promote to semver only at release boundary.

## Commit Package Contract

1. `pkg` must be cohesive and cherry-pick safe.
2. `pkg` must declare touched domain, risk class, and expected blast radius.
3. `pkg` must include validation evidence and fix-forward guidance.
4. `pkg` must avoid mixing unrelated domains.

## PR Branch Topology

1. `lane/<id>-<goal>`
2. `pkg/<domain>-<seq>`
3. `int/<wave>-merge-train`
4. `hotfix/<id>`

Long-lived canary or package-tracking worktrees must be refreshed. See `UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md` for the canonical command surface and rule details. The named `task quality:governance:canary-refresh` entrypoint wraps the same policy for local and CI use. This policy stays focused on commit strategy, versioning, and PR topology.

## Merge Policy

1. `XS` and `S`: squash allowed if auditability is preserved.
2. `M`: preserve bounded history until lane integration.
3. `L` and `XL`: preserve package boundaries; no blind squash.
4. All final merges route through integration worktree controls.

## Conflict Policy

1. Use file-claim/ownership checks before edits.
2. On conflict, fork/branch both outcomes and retain both artifacts.
3. Never destructively overwrite concurrent work.
