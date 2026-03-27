#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for f in \
  "$repo_root/contracts/template.manifest.json" \
  "$repo_root/contracts/reconcile.rules.yaml" \
  "$repo_root/Taskfile.yml" \
  "$repo_root/scripts/validate-foundation.sh" \
  "$repo_root/scripts/validate-domains.sh"; do
  if [ ! -f "$f" ]; then
    echo "[FAIL] missing required file: $f"
    exit 1
  fi
done

echo "[OK] scaffold smoke passed"
