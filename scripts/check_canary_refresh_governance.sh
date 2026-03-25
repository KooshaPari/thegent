#!/usr/bin/env sh
set -eu

ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[CHECK] canary refresh governance policy"

rg -n 'thegent worktree refresh|worktree_governance.sh refresh' docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md
rg -n 'single source of truth for long-lived PR lanes, canary branches, and high-extreme package branches' docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md
rg -n 'CI enforces the same rule through' docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md
rg -n 'CI workflow enforces that policy via' docs/governance/GOVERNANCE_SUMMARY.md
rg -n 'task quality:governance:canary-refresh' .github/workflows/ci.yml
rg -n 'Assert canary refresh governance policy' .github/workflows/ci.yml
rg -n 'quality:governance:canary-refresh' Taskfile.yml
rg -n 'task quality:pre-push:strict-governance' hooks/pre-push-quality.sh
rg -n 'quality:governance:policy:strict|quality:governance:canary-refresh|quality:governance:worktree-inventory|quality:governance:worktree-inventory:strict|quality:governance:legacy-remediation-report' Taskfile.yml

echo "[OK] canary refresh governance policy checks passed"
