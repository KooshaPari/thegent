# thegent managed user shell profile
# Canonical zsh config — managed by thegent dotfiles
# Local overrides: ~/.zshrc.local (never overwritten)

# Load zsh plugins immediately (for compatibility with diagnostic tools)
# These MUST load before the interactive check so diagnostic tools can detect them
[[ -f "${HOME}/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && \
    source "${HOME}/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"

# zsh-syntax-highlighting MUST be last (after all other plugins)
[[ -f "${HOME}/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && \
    source "${HOME}/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

# Early exit for non-interactive shells
[[ $- != *i* ]] && return

# ── Path setup ────────────────────────────────────────────────────────────────
export PATH="${HOME}/.local/bin:${PATH}"
export PATH="${HOME}/bin:${PATH}"

# Homebrew (Apple Silicon)
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# mise (tool version manager)
if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh)"
fi

# ── Shell options ─────────────────────────────────────────────────────────────
setopt AUTO_CD              # cd by typing directory name
setopt CORRECT              # spell correction
setopt HIST_VERIFY          # Don't execute expanded history immediately
setopt SHARE_HISTORY        # Share history between sessions
setopt HIST_IGNORE_DUPS     # Don't record duplicate entries
setopt HIST_IGNORE_SPACE    # Don't record entries starting with a space
setopt EXTENDED_GLOB        # Use extended glob syntax

export HISTSIZE=50000
export SAVEHIST=50000
export HISTFILE="${HOME}/.zsh_history"

# ── Completions ───────────────────────────────────────────────────────────────
autoload -Uz compinit add-zsh-hook

_compinit_deferred() {
    add-zsh-hook -d precmd _compinit_deferred
    if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
        compinit -d "${ZDOTDIR:-$HOME}/.zcompdump" 2>/dev/null
    else
        compinit -C -d "${ZDOTDIR:-$HOME}/.zcompdump" 2>/dev/null
    fi
}
add-zsh-hook precmd _compinit_deferred

# ── Plugins (deferred) ────────────────────────────────────────────────────────
_load_plugins_deferred() {
    add-zsh-hook -d precmd _load_plugins_deferred
    [[ -f "${HOME}/.zsh/plugins/fzf-tab/fzf-tab.plugin.zsh" ]] && \
        source "${HOME}/.zsh/plugins/fzf-tab/fzf-tab.plugin.zsh"
    [[ -f "${HOME}/.zsh/plugins/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh" ]] && \
        source "${HOME}/.zsh/plugins/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh"
}
add-zsh-hook precmd _load_plugins_deferred

# ── Prompt: starship (deferred) ───────────────────────────────────────────────
PS1='%n@%m %1~ %# '

_load_starship_deferred() {
    add-zsh-hook -d precmd _load_starship_deferred
    if command -v starship >/dev/null 2>&1; then
        eval "$(starship init zsh 2>/dev/null)"
    elif [[ -f "${HOME}/.zsh/themes/powerlevel10k/powerlevel10k.zsh-theme" ]]; then
        source "${HOME}/.zsh/themes/powerlevel10k/powerlevel10k.zsh-theme" 2>/dev/null
    fi
}
add-zsh-hook precmd _load_starship_deferred

# ── Aliases ───────────────────────────────────────────────────────────────────
[[ -f "${HOME}/.aliases.sh" ]] && source "${HOME}/.aliases.sh"

# ── Editor ────────────────────────────────────────────────────────────────────
if command -v cursor >/dev/null 2>&1; then
  export EDITOR="cursor --wait"
  export VISUAL="cursor"
elif command -v code >/dev/null 2>&1; then
  export EDITOR="code --wait"
  export VISUAL="code"
else
  export EDITOR="vim"
  export VISUAL="vim"
fi

# ── Tools ─────────────────────────────────────────────────────────────────────
# fzf
if command -v fzf >/dev/null 2>&1; then
  eval "$(fzf --zsh 2>/dev/null)"
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
  export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
  export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
fi

# zoxide (smart cd)
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

# direnv
if command -v direnv >/dev/null 2>&1; then
  eval "$(direnv hook zsh)"
fi

# bat → cat alias
if command -v bat >/dev/null 2>&1; then
  alias cat='bat --paging=never'
fi

# eza → ls alias
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons'
  alias ll='eza --icons -l'
  alias la='eza --icons -la'
  alias tree='eza --tree --icons'
fi

# bun
if command -v bun >/dev/null 2>&1; then
  export BUN_INSTALL="${HOME}/.bun"
  export PATH="${BUN_INSTALL}/bin:${PATH}"
fi

# ── thegent notifications ─────────────────────────────────────────────────────
export THGENT_NOTIFY_ENABLE=1
export THGENT_NOTIFY_VOICE_MODE=all
export THGENT_NOTIFY_COOLDOWN_SEC=8

# ── Local overrides (never overwritten by thegent) ────────────────────────────
[[ -f "${HOME}/.zshrc.local" ]] && source "${HOME}/.zshrc.local"
