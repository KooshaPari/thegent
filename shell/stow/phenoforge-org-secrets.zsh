#!/bin/zsh
# phenoforge-org-secrets.zsh — loader for org-level service credentials.
#
# IMPORTANT: This file MUST NOT contain literal secret values. Secrets live
# in a gitignored local env file (~/.config/phenotype/org-secrets.env or
# ${PHENOFORGE_SECRETS_FILE}) and are loaded into the shell env at runtime.
#
# Recommended local setup (one-time, on each dev machine):
#
#   mkdir -p ~/.config/phenotype
#   cat > ~/.config/phenotype/org-secrets.env <<'ENV'
#   # values from the team's password manager (1Password vault: "Phenoforge")
#   export AUTHKIT_DOMAIN="https://<your-authkit-domain>"
#   export OPENROUTER_API_KEY="<key from 1Password>"
#   export WORKOS_API_KEY="<key from 1Password>"
#   export WORKOS_CLIENT_ID="<client id from 1Password>"
#   ENV
#   chmod 600 ~/.config/phenotype/org-secrets.env
#
# Optional override: set PHENOFORGE_SECRETS_FILE in your shell rc to point
# at an alternate env file (e.g., a worktree-scoped override).

: "${PHENOFORGE_SECRETS_FILE:=${HOME}/.config/phenotype/org-secrets.env}"

if [[ -r "${PHENOFORGE_SECRETS_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${PHENOFORGE_SECRETS_FILE}"
elif [[ -n "${PHENOFORGE_SECRETS_DEBUG:-}" ]]; then
  print -u2 "phenoforge-org-secrets: ${PHENOFORGE_SECRETS_FILE} not readable; secrets unset"
fi
