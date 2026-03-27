#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
repos=(
  template-commons
  template-lang-python
  template-lang-go
  template-lang-typescript
  template-lang-rust
  template-lang-mojo
  template-lang-zig
  template-lang-swift
  template-lang-kotlin
  template-lang-elixir-hex
)

for repo in "${repos[@]}"; do
  path="$root/$repo"
  echo "[CHECK] $repo"
  test -f "$path/contracts/template.manifest.json"
  test -f "$path/contracts/reconcile.rules.yaml"
  test -f "$path/Taskfile.yml"
  bash "$path/scripts/scaffold-smoke.sh"
  echo "[OK] $repo"
done

echo "[OK] foundation validation complete"
