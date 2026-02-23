#!/usr/bin/env sh
set -eu

ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"
METRICS_FILE="${THGENT_GOV_METRICS_FILE:-$ROOT_DIR/var/metrics/governance_policy_metrics.jsonl}"

emit_metric() {
  metric_name="$1"
  metric_value="$2"
  mkdir -p "$(dirname "$METRICS_FILE")"
  printf '{"ts":"%s","metric":"%s","value":%s}\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$metric_name" "$metric_value" >>"$METRICS_FILE"
}

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

if [ ! -x scripts/worktree_governance.sh ]; then
  echo "[FAIL] scripts/worktree_governance.sh missing or not executable" >&2
  failed=1
else
  wt_output="$(./scripts/worktree_governance.sh check 2>&1)" || wt_rc=$?
  wt_rc="${wt_rc:-0}"
  printf '%s\n' "$wt_output"
  warn_count="$(printf '%s\n' "$wt_output" | rg -c "^\[WARN\]" || true)"
  if [ "${warn_count:-0}" -gt 0 ]; then
    emit_metric "worktree_policy_warn_total" "${warn_count}"
  fi
  if [ "$wt_rc" -ne 0 ]; then
    emit_metric "worktree_policy_fail_total" 1
    failed=1
  else
    emit_metric "worktree_policy_pass_total" 1
  fi
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "[OK] governance policy checks passed"
