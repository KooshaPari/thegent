#!/usr/bin/env bash
# qa-tier-enforcer.sh
# Enforces tier-based QA methodology requirements from project .claude/quality.json.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
ATTEST="$PROJECT_DIR/.claude/verification/qa-attestation.json"
FAIL_CLOSED="${QA_TIER_FAIL_CLOSED:-true}"

[[ -f "$QFILE" ]] || exit 0
[[ -f "$ATTEST" ]] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

tier="$(jq -r '.criticality_tier // "established"' "$QFILE")"

case "$tier" in
  new)
    required='["unit","integration","security"]'
    ;;
  established)
    required='["unit","integration","e2e","security"]'
    ;;
  critical)
    required='["unit","integration","e2e","property_based","contract","mutation","security"]'
    ;;
  *)
    required='["unit","integration","security"]'
    ;;
esac

detected="$(jq '.predicate.methodology.detected_test_types // {}' "$ATTEST")"
missing="$(jq -n --argjson req "$required" --argjson det "$detected" '$req | map(select(($det[.] // false) != true))')"
count="$(jq 'length' <<< "$missing")"

signed_present="$(jq -r '.security.signed_attestation_present // false' "$ATTEST")"
slsa_present="$(jq -r '.security.slsa_provenance_present // false' "$ATTEST")"

extra_violations=()
if [[ "$tier" == "critical" ]]; then
  [[ "$signed_present" != "true" ]] && extra_violations+=("signed_attestation")
  [[ "$slsa_present" != "true" ]] && extra_violations+=("slsa_provenance")
fi
extra_count="${#extra_violations[@]}"

missing_csv="$(jq -r 'join(",")' <<< "$missing")"
echo "TIER ENFORCER: tier=$tier missing=$missing_csv signed=$signed_present slsa=$slsa_present"

if [[ "$FAIL_CLOSED" == "true" && ( "$count" -gt 0 || "$extra_count" -gt 0 ) ]]; then
  echo "TIER ENFORCER FAIL: tier=$tier requires [$missing_csv] — $count missing test type(s), $extra_count extra violation(s)" >&2
  exit 2
fi

exit 0
