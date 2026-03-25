#!/usr/bin/env sh
set -eu

ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

METRICS_FILE="${THGENT_GOV_METRICS_FILE:-$ROOT_DIR/var/metrics/governance_policy_metrics.jsonl}"
REQUIRED_POLICY_MARKER="$ROOT_DIR/.thegent-primary-main"

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
docs/governance/MCP_A2A_CONTROL_PLANE_BOUNDARY.md
docs/governance/ROLLOUT_PHASES_CHECKLIST.md
"

require_doc_contains() {
  doc_path="$1"
  needle="$2"
  label="$3"
  if ! rg -qF "$needle" "$doc_path"; then
    echo "[FAIL] ${label}: missing canonical policy text in ${doc_path}" >&2
    failed=1
  fi
}

failed=0
warn_total=0

for f in $required_files; do
  if [ ! -f "$f" ]; then
    echo "[FAIL] missing governance file: $f" >&2
    failed=1
  fi
done

current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [ -z "$current_branch" ] || [ "$current_branch" != "main" ]; then
  echo "[FAIL] Governance precondition: primary checkout must be on main (found: ${current_branch:-unknown})" >&2
  failed=1
fi

if [ ! -f "$REQUIRED_POLICY_MARKER" ]; then
  echo "[FAIL] Governance precondition: missing ${REQUIRED_POLICY_MARKER}" >&2
  failed=1
elif ! rg -q "Keep this repository checkout on main" "$REQUIRED_POLICY_MARKER"; then
  echo "[FAIL] Governance marker is malformed: expected policy text in .thegent-primary-main" >&2
  failed=1
elif ! rg -q "Use dedicated worktrees for branch development" "$REQUIRED_POLICY_MARKER"; then
  echo "[FAIL] Governance marker is malformed: expected branch-worktree policy in .thegent-primary-main" >&2
  failed=1
fi

if ! rg -q "WORKTREE_AND_DELEGATION_INDEX\\.md" AGENTS.md; then
  echo "[FAIL] AGENTS.md must reference docs/governance/WORKTREE_AND_DELEGATION_INDEX.md" >&2
  failed=1
fi

if ! rg -q "THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE" scripts/bootstrap.sh; then
  echo "[FAIL] scripts/bootstrap.sh missing THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE enforcement path" >&2
  failed=1
fi

if ! rg -q "quality:governance:canary-refresh:" Taskfile.yml; then
  echo "[FAIL] Taskfile.yml missing quality:governance:canary-refresh task" >&2
  failed=1
fi

if ! rg -q "quality:governance:worktree-inventory:" Taskfile.yml; then
  echo "[FAIL] Taskfile.yml missing quality:governance:worktree-inventory task" >&2
  failed=1
fi

if ! rg -q "quality:governance:worktree-inventory:strict:" Taskfile.yml; then
  echo "[FAIL] Taskfile.yml missing quality:governance:worktree-inventory:strict task" >&2
  failed=1
fi

if ! rg -q "quality:governance:legacy-remediation-report:" Taskfile.yml; then
  echo "[FAIL] Taskfile.yml missing quality:governance:legacy-remediation-report task" >&2
  failed=1
fi

if ! rg -q "quality:pre-push:strict-governance:" Taskfile.yml; then
  echo "[FAIL] Taskfile.yml missing quality:pre-push:strict-governance task" >&2
  failed=1
fi

if [ ! -x scripts/worktree_governance.sh ]; then
  echo "[FAIL] scripts/worktree_governance.sh missing or not executable" >&2
  failed=1
else
  allow_legacy="${THGENT_WORKTREE_ALLOW_LEGACY:-0}"
  wt_rc=0
  wt_output="$(THGENT_WORKTREE_ALLOW_LEGACY="$allow_legacy" ./scripts/worktree_governance.sh check 2>&1)" || wt_rc=$?
  printf '%s\n' "$wt_output"
  warn_total="$(printf '%s\n' "$wt_output" | rg -c "^\[WARN\]" || true)"
  warn_total="${warn_total:-0}"
  if [ "$allow_legacy" = "0" ] && printf '%s\n' "$wt_output" | rg -q "^\[WARN\]"; then
    echo "[FAIL] Governance precondition: legacy worktree mode is not allowed." >&2
    failed=1
  fi
  if [ "$wt_rc" -ne 0 ]; then
    failed=1
  fi
fi

require_doc_contains \
  docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md \
  "thegent worktree refresh" \
  "worktree refresh command"
require_doc_contains \
  docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md \
  "thegent worktree migrate-legacy" \
  "legacy migration command"
require_doc_contains \
  docs/governance/UNIFIED_WORKTREE_WORKFLOW_GOVERNANCE.md \
  "thegent_worktree" \
  "MCP parity"
require_doc_contains \
  docs/governance/WORKTREE_SCALE_COMMIT_VERSION_PR_POLICY.md \
  "Long-lived canary or package-tracking worktrees must be refreshed" \
  "canary refresh policy"
require_doc_contains \
  docs/governance/GOVERNANCE_SUMMARY.md \
  "task quality:governance:canary-refresh" \
  "governance summary canary rule"
require_doc_contains \
  docs/governance/GOVERNANCE_SUMMARY.md \
  'legacy worktrees are reported separately through `task quality:governance:legacy-remediation-report`' \
  "governance summary legacy remediation rule"

if [ "$warn_total" -gt 0 ]; then
  emit_metric "worktree_policy_warn_total" "$warn_total"
fi

if [ "$failed" -eq 0 ]; then
  pass_total=1
  fail_total=0
else
  pass_total=0
  fail_total=1
fi

echo "[SUMMARY] governance policy checks: pass=$pass_total fail=$fail_total warn=$warn_total"

if [ "$failed" -ne 0 ]; then
  emit_metric "worktree_policy_fail_total" 1
  emit_metric "worktree_policy_pass_total" 0
else
  emit_metric "worktree_policy_pass_total" 1
  emit_metric "worktree_policy_fail_total" 0
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "[OK] governance policy checks passed"
