# Phenotype MiniMax + CLIProxy env helpers for Claude Code and Codex (zsh/bash).
# Source from ~/.zshrc.local — see docs/research/SECRETS_MINIMAX_CLIPROXY_MESH_RUNBOOK_2026-03-29.md
#
# shellcheck shell=bash disable=SC3046

: "${PHENOTYPE_MINIMAX_MODEL:=minimax-m2.7-highspeed}"
: "${PHENOTYPE_SOPS_SECRETS:=${HOME}/.config/phenotype/secrets.env}"
: "${PHENOTYPE_CLIPROXY_HOST:=127.0.0.1}"
: "${PHENOTYPE_CLIPROXY_PORT:=8317}"
: "${PHENOTYPE_VAULT_MINIMAX_PATH:=secret/phenotype/minimax}"
: "${PHENOTYPE_VAULT_MINIMAX_FIELD:=api_key}"

_phenotype_minimax_key() {
  if [[ -n "${MINIMAX_API_KEY:-}" ]]; then
    printf '%s' "$MINIMAX_API_KEY"
    return 0
  fi

  if command -v vault >/dev/null 2>&1 && [[ -n "${VAULT_ADDR:-}" ]] && [[ -n "${VAULT_TOKEN:-}" ]]; then
    local v
    v="$(vault kv get -field="${PHENOTYPE_VAULT_MINIMAX_FIELD}" "${PHENOTYPE_VAULT_MINIMAX_PATH}" 2>/dev/null || true)"
    if [[ -n "$v" ]]; then
      printf '%s' "$v"
      return 0
    fi
  fi

  if command -v sops >/dev/null 2>&1 && [[ -r "$PHENOTYPE_SOPS_SECRETS" ]]; then
    local line
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ "$line" =~ ^[[:space:]]*# ]] && continue
      [[ "$line" == MINIMAX_API_KEY=* ]] || continue
      printf '%s' "${line#MINIMAX_API_KEY=}"
      return 0
    done < <(sops -d --input-type dotenv --output-type dotenv "$PHENOTYPE_SOPS_SECRETS" 2>/dev/null)
  fi

  return 1
}

# mclaude: set MiniMax env vars and run claude with passed arguments
mclaude() {
  local k
  k="$(_phenotype_minimax_key)" || {
    echo "mclaude: set MINIMAX_API_KEY, Vault KV at ${PHENOTYPE_VAULT_MINIMAX_PATH}, or sops file ${PHENOTYPE_SOPS_SECRETS}" >&2
    return 1
  }
  export ANTHROPIC_API_KEY="$k"
  export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
  export CLAUDE_MODEL="$PHENOTYPE_MINIMAX_MODEL"
  exec claude "$@"
}

# mcodex: set MiniMax env vars and run codex with passed arguments
mcodex() {
  local k
  k="$(_phenotype_minimax_key)" || {
    echo "mcodex: set MINIMAX_API_KEY, Vault KV at ${PHENOTYPE_VAULT_MINIMAX_PATH}, or sops file ${PHENOTYPE_SOPS_SECRETS}" >&2
    return 1
  }
  export OPENAI_API_KEY="$k"
  export OPENAI_BASE_URL="https://api.minimax.io/v1"
  export CODEX_MODEL="$PHENOTYPE_MINIMAX_MODEL"
  exec codex "$@"
}

# vclaude: set CLIProxy env vars and run claude with passed arguments
vclaude() {
  export ANTHROPIC_API_KEY="${PHENOTYPE_CLIPROXY_DUMMY_KEY:-dummy-not-used}"
  export ANTHROPIC_BASE_URL="http://${PHENOTYPE_CLIPROXY_HOST}:${PHENOTYPE_CLIPROXY_PORT}/v1"
  export CLAUDE_MODEL="$PHENOTYPE_MINIMAX_MODEL"
  exec claude "$@"
}

# vcodex: set CLIProxy env vars and run codex with passed arguments
vcodex() {
  export OPENAI_API_KEY="${PHENOTYPE_CLIPROXY_DUMMY_KEY:-dummy-not-used}"
  export OPENAI_BASE_URL="http://${PHENOTYPE_CLIPROXY_HOST}:${PHENOTYPE_CLIPROXY_PORT}/v1"
  export CODEX_MODEL="$PHENOTYPE_MINIMAX_MODEL"
  exec codex "$@"
}

phenotype_harness_unload() {
  unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL CLAUDE_MODEL OPENAI_API_KEY OPENAI_BASE_URL CODEX_MODEL
}
