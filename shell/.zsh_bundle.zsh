# thegent managed zsh bundle (sourced from ~/.zshrc and ~/.zshenv)
# Full comprehensive setup: utilities, aliases, safe path handling.

zmodload zsh/datetime 2>/dev/null || true

typeset -gU path fpath cdpath

_thegent_missing_path_error() {
  print -r -- "$1: no such file or directory: $2" >&2
}

# --- Path-safe utilities ---
qls() {
  local target="${1:-.}"
  if [[ -z "$target" ]]; then
    command ls
    return 0
  fi
  if [[ -e "$target" ]]; then
    command ls -lah "$target"
    return 0
  fi
  _thegent_missing_path_error "q ls" "$target"
  return 1
}

qfind() {
  local target="${1:-.}"
  if [[ ! -e "$target" ]]; then
    _thegent_missing_path_error "q find" "$target"
    return 1
  fi
  command find "$target" "${@:2}"
}

qgrep() {
  if [[ "$#" -lt 2 ]]; then
    print -r -- "Usage: qgrep PATTERN PATH..."
    return 2
  fi
  local pattern="$1"
  shift
  local missing=0
  for target in "$@"; do
    if [[ ! -e "$target" ]]; then
      _thegent_missing_path_error "qgrep" "$target"
      missing=1
      continue
    fi
    if command -v rg >/dev/null 2>&1; then
      rg --line-number --no-heading --hidden --glob '!.git' --color=never "$pattern" "$target"
    else
      command grep -nH -- "$pattern" "$target"
    fi
  done
  return "$missing"
}

# --- Aliases ---
ll() { qls "$@"; }

# --- Load Shell Optimization (performance: lazy loading, eval caching, profiling) ---
# Optimization handles: lazy loading expensive tools, caching eval outputs, parallel loading
if [[ -f "$HOME/.zsh_optimization.zsh" ]]; then
  source "$HOME/.zsh_optimization.zsh"
elif [[ -f "${(%):-%x:h}/.zsh_optimization.zsh" ]]; then
  source "${(%):-%x:h}/.zsh_optimization.zsh"
fi

# --- Load Shell Safeguards (comprehensive protection) ---
# Safeguards handle: ls aliasing, fork explosions, timeouts, eval security, resource limits
if [[ -f "$HOME/.zsh_safeguards.zsh" ]]; then
  source "$HOME/.zsh_safeguards.zsh"
elif [[ -f "${(%):-%x:h}/.zsh_safeguards.zsh" ]]; then
  source "${(%):-%x:h}/.zsh_safeguards.zsh"
fi

# --- Load Advanced Shell Optimization (instant prompt, async loading, advanced caching) ---
# Advanced features: instant prompt, async/turbo loading, multi-level caching, error recovery,
# background job management, cross-platform compatibility, advanced monitoring
if [[ -f "$HOME/.zsh_advanced.zsh" ]]; then
  source "$HOME/.zsh_advanced.zsh"
elif [[ -f "${(%):-%x:h}/.zsh_advanced.zsh" ]]; then
  source "${(%):-%x:h}/.zsh_advanced.zsh"
fi

# --- Navigation (safe, no-op on missing) ---
cdq() {
  if [[ -d "${1:-.}" ]]; then
    builtin cd "$1" || return 1
  else
    _thegent_missing_path_error "cdq" "${1:-.}"
    return 1
  fi
}

# --- Interactive-only: bindkeys ---
if [[ -z "${AGENT_ID:-}" && -n "${PS1:-}" ]]; then
  bindkey -e
fi

export THEGENT_BUNDLE_LOADED=1
