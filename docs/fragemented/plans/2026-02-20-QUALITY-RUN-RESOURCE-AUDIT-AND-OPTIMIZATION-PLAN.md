# Plan: Quality Run Resource Audit and Optimization (2026-02-20)

## 1. Audit Summary

Observed local risk indicators:

1. Workspace disk is saturated (`/System/Volumes/Data` at 100%).
2. Repository has very high transient directory cardinality (`.shadow-*` count: 254).
3. Shared quality gate runs unbounded repository scans:
   - `jscpd` scans `.` recursively.
   - `gitleaks detect --no-git` scans regular files recursively.
   - slop check uses recursive grep patterns on `.`.
4. Agent-assisted quality scripts can loop indefinitely with `-r` (reload-until-green) and pass full output payload each attempt.

Primary failure pattern:

1. Unbounded recursive scanners + massive transient trees produce runaway IO/CPU and large temp/log churn.
2. Infinite reload loops amplify the same expensive run repeatedly.

## 2. External Reference Notes

1. `jscpd` supports `--gitignore`, `--ignore`, `--max-lines`, `--max-size`, `--noSymlinks`.
2. `gitleaks detect` supports `--source`, `--max-target-megabytes`, `--timeout`, `--no-git`.
3. `ruff` default behavior excludes common caches/build dirs; custom recursive checks should mirror equivalent excludes.

## 3. Optimization Strategy

### P1: Bound Scanner Scope

1. Add `.jscpd.json` with explicit ignore globs for transient/generated/cached trees.
2. Move duplication check to config-driven `jscpd` invocation.
3. Add `gitleaks` file-size and runtime caps.
4. Replace slop-check recursive grep with `rg` + explicit ignore globs.

### P2: Bound Retry Loops

1. Add `QUALITY_MAX_ATTEMPTS` (default `3`) to `quality-agent.sh` and `quality-fix-agent.sh`.
2. Add `QUALITY_MAX_PROMPT_CHARS` (default `20000`) to cap payload size to agent handoffs.

### P3: Bound Parallelism and Step Runtime

1. Add `QUALITY_MAX_WORKERS` (default `4`) in DAG runner.
2. Add `QUALITY_STEP_TIMEOUT_SEC` (default `600`) in DAG runner.

## 4. Acceptance Criteria

1. `task quality:gate` no longer scans `.shadow-*`, `.git-cache`, `.venv*`, `.worktrees`, `node_modules`, build/cache dirs for duplication/slop checks.
2. Security scan has bounded file-size and timeout.
3. `quality-a-r` and fix reload loops terminate deterministically after max attempts.
4. DAG runner parallelism is capped and tunable via env vars.
5. No fallback/silent-pass logic added; failures remain explicit.

## 5. Follow-up Operational Recommendation

1. Add periodic cleanup of stale `.shadow-*` directories and `.quality/logs` retention.
2. Keep quality scans targeted to tracked/source trees when running locally on constrained disks.
