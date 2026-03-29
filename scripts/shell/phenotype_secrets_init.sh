#!/usr/bin/env bash
# Optional: create ~/.local/state/phenotype/secrets and a plaintext template for sops encryption.
set -euo pipefail
DEST="${PHENOTYPE_SECRETS_DIR:-$HOME/.local/state/phenotype/secrets}"
REPO="${PHENOTYPE_REPOS_ROOT:-$HOME/CodeProjects/Phenotype/repos}"
EXAMPLE="$REPO/thegent/templates/secrets/phenotype-secrets.env.example"
mkdir -p "$DEST"
README="$DEST/README.txt"
if [[ ! -f "$README" ]]; then
  cat >"$README" <<'EOF'
Phenotype local credential material (never commit plaintext).

Policy: ZDR/BYOK per org; see docs/reference/CANONICAL_INVARIANT_PROSE.md.

1. cp phenotype-secrets.env.in secrets.env  &&  $EDITOR secrets.env
2. sops encrypt (see thegent/templates/secrets/sops-phenotype-config.yaml.example)
3. export PHENOTYPE_SOPS_SECRETS=$HOME/.local/state/phenotype/secrets/secrets.env.age

Factory users may store BYOK in ~/.factory instead of this path.
EOF
fi
IN="$DEST/secrets.env.in"
if [[ ! -f "$IN" ]] && [[ -r "$EXAMPLE" ]]; then
  cp "$EXAMPLE" "$IN"
  echo "Created $IN — set MINIMAX_API_KEY if using shell harness without Factory BYOK."
elif [[ -f "$IN" ]]; then
  echo "Already exists: $IN"
else
  echo "Missing template $EXAMPLE"
fi
