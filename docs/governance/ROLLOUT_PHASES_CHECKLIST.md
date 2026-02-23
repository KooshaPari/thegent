# Governance Rollout Phases Checklist

## Phase 1 (10 percent lanes)

1. Enable governance policy checks in pilot lanes.
2. Produce worktree inventory artifacts daily.
3. Track pass/fail/warn counters for policy checks.
4. Validate local and CI parity for pre-push gates.

## Phase 2 (50 percent lanes)

1. Expand strict worktree policy to half of active lanes.
2. Enforce classifier-based delegation contracts for pilot domains.
3. Require protocol boundary artifacts on merged PR branches.
4. Run migration tool in apply mode for selected repositories.

## Phase 3 (100 percent lanes)

1. Remove legacy override (`THGENT_WORKTREE_ALLOW_LEGACY`) from default workflows.
2. Enforce strict worktree naming/root policy globally.
3. Make governance metrics SLOs mandatory release gate criteria.
4. Require release signoff bundle with governance artifacts.

