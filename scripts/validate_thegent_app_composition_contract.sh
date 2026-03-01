#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

REQUIRED_FILES=(
  "docs/changes/shared-modules/thegent-app-composition-v1/proposal.md"
  "docs/changes/shared-modules/thegent-app-composition-v1/tasks.md"
  "docs/contracts/thegent-app-composition.contract.json"
  "docs/guides/thegent-app-composition-boundary.md"
)

REQUIRED_KEYS=(
  "contract_name"
  "version"
  "scope"
  "allowed_orchestration_responsibilities"
  "disallowed_domain_ownership"
  "external_domain_modules"
  "migration_checkpoints"
)

failures=0

echo "[validate] thegent app composition contract artifacts"
echo "[validate] root: ${ROOT_DIR}"

for rel_path in "${REQUIRED_FILES[@]}"; do
  abs_path="${ROOT_DIR}/${rel_path}"
  if [[ -f "${abs_path}" ]]; then
    echo "[ok] file exists: ${rel_path}"
  else
    echo "[error] missing file: ${rel_path}"
    failures=$((failures + 1))
  fi
done

contract_path="${ROOT_DIR}/docs/contracts/thegent-app-composition.contract.json"
if [[ -f "${contract_path}" ]]; then
  for key in "${REQUIRED_KEYS[@]}"; do
    if python3 -c 'import json,sys; data=json.load(open(sys.argv[1])); sys.exit(0 if sys.argv[2] in data else 1)' "${contract_path}" "${key}"; then
      echo "[ok] contract key present: ${key}"
    else
      echo "[error] missing contract key: ${key}"
      failures=$((failures + 1))
    fi
  done
fi

if [[ ${failures} -ne 0 ]]; then
  echo "[result] FAIL (${failures} issue(s))"
  exit 1
fi

echo "[result] PASS"
