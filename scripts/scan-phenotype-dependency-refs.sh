#!/usr/bin/env bash
# Scan Phenotype/repos for manifest references to phenotype-* and common patterns.
# Usage: from Phenotype/repos: bash scripts/scan-phenotype-dependency-refs.sh
# Output: Markdown table to stdout (redirect to file if desired).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "# Phenotype dependency reference scan"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "## Manifests mentioning phenotype-"
echo ""
echo "| File |"
echo "|------|"

if command -v rg >/dev/null 2>&1; then
  rg -l 'phenotype-' --glob 'go.mod' --glob 'package.json' --glob 'Cargo.toml' --glob 'pyproject.toml' --glob 'package.yaml' 2>/dev/null | sort -u | while read -r f; do
    echo "| \`$f\` |"
  done || true
else
  echo "| (install ripgrep: \`rg\`) |"
fi

echo ""
echo "## Import / reference hints (sample)"
echo ""
echo "| Pattern | Count (approx) |"
echo "|---------|----------------|"
if command -v rg >/dev/null 2>&1; then
  c1=$(rg -c 'github\.com/.*/phenotype-' --glob '*.{go,ts,tsx}' 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  c2=$(rg -c '@phenotype/' --glob '*.{ts,tsx,js}' 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  echo "| go import path | $c1 |"
  echo "| npm scope @phenotype/ | $c2 |"
else
  echo "| — | rg not found |"
fi

echo ""
echo "_Full graph: combine with per-repo \`go mod graph\`, \`cargo tree\`, etc._"
