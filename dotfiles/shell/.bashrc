# dotfiles/shell/.bashrc
# Phenotype/thegent canonical bash configuration
# Install: ln -sf "$DOTFILES_DIR/shell/.bashrc" ~/.bashrc

# Skip for non-interactive shells
[[ $- != *i* ]] && return

# --- XDG Base Directory ---
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"

# --- History ---
export HISTFILE="${XDG_DATA_HOME}/bash/history"
mkdir -p "$(dirname "$HISTFILE")"
export HISTSIZE=50000
export HISTFILESIZE=50000
export HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# --- Path ---
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

# --- mise (polyglot version manager) ---
if command -v mise &>/dev/null; then
  eval "$(mise activate bash 2>/dev/null)" || true
elif [[ -x "$HOME/.local/bin/mise" ]]; then
  eval "$("$HOME/.local/bin/mise" activate bash 2>/dev/null)" || true
fi

# --- Dotfiles location ---
export DOTFILES_DIR="${DOTFILES_DIR:-$HOME/.dotfiles}"

# --- Load Aliases ---
[[ -f "$DOTFILES_DIR/shell/aliases.sh" ]] && source "$DOTFILES_DIR/shell/aliases.sh"

# --- fzf ---
if command -v fzf &>/dev/null; then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
  export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
  eval "$(fzf --bash 2>/dev/null)" || true
fi

# --- Local overrides (never commit this file) ---
[[ -f "$HOME/.bashrc.local" ]] && source "$HOME/.bashrc.local"
[[ -f "$HOME/.bashrc.secrets" ]] && source "$HOME/.bashrc.secrets"
