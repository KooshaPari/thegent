#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
repos=(template-domain-webapp template-domain-service-api)

for repo in "${repos[@]}"; do
  path="$root/$repo"
  echo "[CHECK] $repo"
  test -f "$path/contracts/template.manifest.json"
  test -f "$path/contracts/reconcile.rules.yaml"
  test -f "$path/Taskfile.yml"
  bash "$path/scripts/scaffold-smoke.sh"
  echo "[OK] $repo"
done

echo "[OK] domain validation complete"
