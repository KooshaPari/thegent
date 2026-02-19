# thegent managed user shell profile
# Comprehensive, optimal shell configuration (canonical)
# Install target for per-user shell customization.

# Early exit for non-interactive shells
[[ -z "${PS1:-}" ]] && return

# Source base configs (system environment, core utilities, safeguards)
[[ -f "$HOME/.zshenv" ]] && source "$HOME/.zshenv"
[[ -f "$HOME/.zsh_bundle.zsh" ]] && source "$HOME/.zsh_bundle.zsh"

# Load safeguards in interactive shells only
if [[ -n "${PS1:-}" ]] && [[ -f "$HOME/.zsh_safeguards.zsh" ]]; then
  source "$HOME/.zsh_safeguards.zsh"
fi

# Lazy-load completions (optimized: skip security check for speed, defer for <50ms startup)
# Only run full compinit once per day, otherwise use -C (skip security check)
# Defer compinit until after prompt to avoid blocking startup
autoload -Uz compinit add-zsh-hook
_compinit_deferred() {
    add-zsh-hook -d precmd _compinit_deferred
    if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
        compinit -d "${ZDOTDIR:-$HOME}/.zcompdump" 2>/dev/null
    else
        compinit -C -d "${ZDOTDIR:-$HOME}/.zcompdump" 2>/dev/null
    fi
}
if [[ -n "${PS1:-}" ]]; then
    add-zsh-hook precmd _compinit_deferred
fi

# Use Bun if available (fastest JS runtime)
if command -v bun >/dev/null 2>&1; then
    export USE_BUN_TOOLS=1
    # Note: Keep node for tools that require it (e.g., VitePress)
    # Users can alias in .zshrc.local if desired
fi

# direnv REMOVED - fully migrated to mise (mise handles all environment management)
# mise is faster (<50ms) and more reliable than direnv (3-4s startup delay)

# Lazy-load plugins (deferred until after prompt, only in interactive shells)
# Note: Background jobs (&) don't work for source, so we defer loading until after first prompt
if [[ -n "${PS1:-}" ]]; then
    # Defer plugin loading until after prompt appears (using precmd hook)
    _load_plugins_deferred() {
        # Ensure add-zsh-hook is available
        autoload -Uz add-zsh-hook
        # Remove this hook after first run
        add-zsh-hook -d precmd _load_plugins_deferred
        
        # Load plugins synchronously (fast enough after prompt is shown)
        # fzf-tab (load after compinit)
        [[ -f "${HOME}/.zsh/plugins/fzf-tab/fzf-tab.plugin.zsh" ]] && \
            source "${HOME}/.zsh/plugins/fzf-tab/fzf-tab.plugin.zsh"
        
        # zsh-autosuggestions
        [[ -f "${HOME}/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && \
            source "${HOME}/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
        
        # fast-syntax-highlighting (load last)
        [[ -f "${HOME}/.zsh/plugins/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh" ]] && \
            source "${HOME}/.zsh/plugins/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh"
    }
    add-zsh-hook precmd _load_plugins_deferred
    
    # Prompt: starship (cross-shell, fast) - DEFERRED for <50ms startup
    # Defer starship initialization until after first prompt to avoid blocking startup
    # Use minimal prompt initially, then load starship async after prompt appears
    PS1='%n@%m %1~ %# '
    
    _load_starship_deferred() {
        # Ensure add-zsh-hook is available
        autoload -Uz add-zsh-hook
        # Remove this hook after first run
        add-zsh-hook -d precmd _load_starship_deferred
        
        # Load starship synchronously (but after prompt is shown)
        if command -v starship >/dev/null 2>&1; then
            eval "$(starship init zsh 2>/dev/null)"
        elif [[ -f "${HOME}/.zsh/themes/powerlevel10k/powerlevel10k.zsh-theme" ]]; then
            source "${HOME}/.zsh/themes/powerlevel10k/powerlevel10k.zsh-theme" 2>/dev/null
        fi
    }
    add-zsh-hook precmd _load_starship_deferred
fi

# Load user customizations (if exists, never overwritten)
if [[ -f "$HOME/.zshrc.local" ]]; then
  source "$HOME/.zshrc.local"
fi

# thegent notifications (managed)
export THGENT_NOTIFY_ENABLE=1
export THGENT_NOTIFY_VOICE_MODE=all
export THGENT_NOTIFY_VOICE_NAME="Siri"
export THGENT_NOTIFY_COOLDOWN_SEC=8
