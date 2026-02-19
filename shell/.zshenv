# thegent managed system shell environment
# This file is a source-of-truth template for the user's `~/.zshenv`.

# Increase FUNCNEST early to prevent nested function errors
export FUNCNEST=1000

# Keep environment setup minimal for all zsh invocations.
typeset -gU path

# Autoload add-zsh-hook early for deferred loading functions
autoload -Uz add-zsh-hook

# Early return for non-human AI sessions (zero-fork UX).
if [[ -n "${AGENT_ID:-}" || -n "${SHARECLI_AGENT_CONTEXT:-}" || -n "${SHARECLI_AGENT:-}" ]]; then
    unsetopt zle 2>/dev/null || true
    return
fi

# Core PATH policy for fast runtime and local tools.
path=(
  "$HOME/.local/bin"
  "$HOME/bin"
  "/opt/homebrew/bin"
  "/opt/homebrew/sbin"
  $path
)
export PATH

# Optional runtime mode defaults (safe fallbacks).
export USE_FAST_RUNTIME="${USE_FAST_RUNTIME:-1}"
export USE_FAST_GIT="${USE_FAST_GIT:-1}"
export USE_BUN_TOOLS="${USE_BUN_TOOLS:-1}"
export USE_FAST_PYTHON="${USE_FAST_PYTHON:-1}"

# Ensure bundle wiring is available once for interactive shells.
if [[ -f "$HOME/.zsh_bundle.zsh" ]]; then
    source "$HOME/.zsh_bundle.zsh"
fi

# Nix (Determinate Systems) - DEFERRED for <50ms startup
# Only load in interactive shells or if explicitly requested
# Skip in non-interactive shells to avoid timeouts
# Defer Nix loading until after prompt (Nix is fast but can be deferred)
if [ -e /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]; then
  # Check if we're in an interactive shell or if NIX_FORCE_LOAD is set
  if [ -n "${PS1:-}" ] || [ -n "${NIX_FORCE_LOAD:-}" ] || [ -t 0 ]; then
    # Defer Nix loading until after prompt appears (non-blocking)
    _load_nix_deferred() {
      # Ensure add-zsh-hook is available
      autoload -Uz add-zsh-hook
      add-zsh-hook -d precmd _load_nix_deferred
      . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh 2>/dev/null || true
    }
    if [[ -n "${PS1:-}" ]]; then
      autoload -Uz add-zsh-hook
      add-zsh-hook precmd _load_nix_deferred
    else
      # Non-interactive: load immediately if NIX_FORCE_LOAD is set
      [[ -n "${NIX_FORCE_LOAD:-}" ]] && . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh 2>/dev/null || true
    fi
  fi
fi

# mise hook (fast environment manager, written in Rust)
# DEFERRED for <50ms startup - mise activation takes ~1s, so defer until after prompt
# Skip in non-interactive shells to prevent hangs
if command -v mise >/dev/null 2>&1 && [[ -n "${PS1:-}" || -t 0 ]]; then
  # Defer mise activation until after prompt appears (non-blocking)
  _load_mise_deferred() {
    # Ensure add-zsh-hook is available
    autoload -Uz add-zsh-hook
    add-zsh-hook -d precmd _load_mise_deferred
    eval "$(mise activate zsh)" 2>/dev/null || true
    export MISE_ENV=1
  }
  if [[ -n "${PS1:-}" ]]; then
    add-zsh-hook precmd _load_mise_deferred
  else
    # Non-interactive: activate immediately if needed
    eval "$(mise activate zsh)" 2>/dev/null || true
    export MISE_ENV=1
  fi
fi

# direnv REMOVED - fully migrated to mise (direnv was 3-4s slower)
