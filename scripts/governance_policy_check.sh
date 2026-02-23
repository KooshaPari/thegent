#!/usr/bin/env sh
set -eu

ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

required_files="
docs/governance/WORKTREE_AND_DELEGATION_INDEX.md
docs/governance/WORKTREE_SCALE_COMMIT_VERSION_PR_POLICY.md
docs/governance/DELEGATION_ARCHITECTURE_LN.md
docs/governance/TASK_CLASSIFIER_SCHEMA.yaml
docs/governance/DOMAIN_PLAYBOOKS.md
docs/governance/GOVERNANCE_ROADMAP_DAG.md
"

failed=0

for f in $required_files; do
  if [ ! -f "$f" ]; then
    echo "[FAIL] missing governance file: $f" >&2
    failed=1
  fi
done

if ! rg -q "WORKTREE_AND_DELEGATION_INDEX\\.md" AGENTS.md; then
  echo "[FAIL] AGENTS.md must reference docs/governance/WORKTREE_AND_DELEGATION_INDEX.md" >&2
  failed=1
fi

if ! rg -q "THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE" scripts/bootstrap.sh; then
  echo "[FAIL] scripts/bootstrap.sh missing THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE enforcement path" >&2
  failed=1
fi

<<<<<<< HEAD
<<<<<<< HEAD
=======
if [ ! -x scripts/worktree_governance.sh ]; then
  echo "[FAIL] scripts/worktree_governance.sh missing or not executable" >&2
  failed=1
else
  if ! ./scripts/worktree_governance.sh check; then
    failed=1
  fi
fi

>>>>>>> codex/governance-wireup
=======
>>>>>>> codex/provider-plane-wave1
if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "[OK] governance policy checks passed"
