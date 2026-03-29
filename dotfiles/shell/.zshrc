# dotfiles/shell/.zshrc
# Phenotype/thegent canonical zsh configuration
# Install: ln -sf "$DOTFILES_DIR/shell/.zshrc" ~/.zshrc

# --- Performance: Profiling (uncomment to debug slow shell) ---
# zmodload zsh/zprof

# --- XDG Base Directory ---
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"

# --- History ---
export HISTFILE="${XDG_DATA_HOME}/zsh/history"
mkdir -p "$(dirname "$HISTFILE")"
export HISTSIZE=50000
export SAVEHIST=50000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_VERIFY
setopt SHARE_HISTORY
setopt EXTENDED_HISTORY

# --- Path ---
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

# --- mise (polyglot version manager) ---
if command -v mise &>/dev/null; then
  eval "$(mise activate zsh 2>/dev/null)" || true
elif [[ -x "$HOME/.local/bin/mise" ]]; then
  eval "$("$HOME/.local/bin/mise" activate zsh 2>/dev/null)" || true
fi

# --- Dotfiles location ---
export DOTFILES_DIR="${DOTFILES_DIR:-$HOME/.dotfiles}"

# --- Load Aliases ---
[[ -f "$DOTFILES_DIR/shell/aliases.sh" ]] && source "$DOTFILES_DIR/shell/aliases.sh"

# --- Load Phenotype aliases if present ---
[[ -f "$DOTFILES_DIR/phenotype/worktree-aliases.sh" ]] && source "$DOTFILES_DIR/phenotype/worktree-aliases.sh"

# --- Completions ---
autoload -U compinit
compinit -d "${XDG_CACHE_HOME}/zsh/zcompdump-$ZSH_VERSION"

# --- Key Bindings ---
bindkey '^[[A' history-search-backward
bindkey '^[[B' history-search-forward
bindkey '^R' history-incremental-search-backward
bindkey '^E' end-of-line
bindkey '^A' beginning-of-line

# --- fzf ---
if command -v fzf &>/dev/null; then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
  export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
  source <(fzf --zsh 2>/dev/null) || true
fi

# --- Starship prompt ---
if command -v starship &>/dev/null; then
  eval "$(starship init zsh)"
fi

# --- TTY self-heal (Ghostty/kitty/extended key mode desync guard) ---
if [[ -o interactive ]]; then
  _thegent_tty_self_heal() {
    stty sane 2>/dev/null || true
    stty intr '^C' quit '^\' erase '^?' kill '^U' 2>/dev/null || true
    [[ -t 1 ]] && printf '\e[>4;0m' || true
    [[ -t 1 ]] && printf '\e[<u' || true
  }
  autoload -Uz add-zsh-hook
  add-zsh-hook precmd _thegent_tty_self_heal
fi

# --- Local overrides (never commit this file) ---
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"

# --- Secrets (never commit this file) ---
[[ -f "$HOME/.zshrc.secrets" ]] && source "$HOME/.zshrc.secrets"

# --- zsh plugins (optional, load last) ---
[[ -f "$HOME/.zshrc.plugins" ]] && source "$HOME/.zshrc.plugins"

# --- Performance: Profiling end ---
# zprof
