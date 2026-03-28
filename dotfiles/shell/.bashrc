# thegent managed — bash config
# For use on servers/WSL where zsh is not available
# Local overrides: ~/.bashrc.local

# Non-interactive shell: exit early
[[ $- != *i* ]] && return

# ── Path setup ────────────────────────────────────────────────────────────────
export PATH="${HOME}/.local/bin:${HOME}/bin:${PATH}"

# Homebrew (Apple Silicon)
[[ -f /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"

# mise
if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate bash)"
fi

# bun
if [[ -d "${HOME}/.bun" ]]; then
  export BUN_INSTALL="${HOME}/.bun"
  export PATH="${BUN_INSTALL}/bin:${PATH}"
fi

# ── History ───────────────────────────────────────────────────────────────────
HISTSIZE=50000
HISTFILESIZE=50000
HISTCONTROL=ignoreboth
shopt -s histappend

# ── Prompt ────────────────────────────────────────────────────────────────────
if command -v starship >/dev/null 2>&1; then
  eval "$(starship init bash 2>/dev/null)"
fi

# ── Aliases ───────────────────────────────────────────────────────────────────
[[ -f "${HOME}/.aliases.sh" ]] && source "${HOME}/.aliases.sh"

# ── Tools ─────────────────────────────────────────────────────────────────────
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash)"
command -v direnv >/dev/null 2>&1 && eval "$(direnv hook bash)"

# ── Local overrides ───────────────────────────────────────────────────────────
[[ -f "${HOME}/.bashrc.local" ]] && source "${HOME}/.bashrc.local"
