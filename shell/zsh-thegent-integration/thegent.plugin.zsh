# thegent.plugin.zsh - Main zsh plugin for thegent integration
# Version: 1.0.0
# Loads: functions, completions, async operations

# Prevent double loading
if [[ -n "$_THEGENT_PLUGIN_LOADED" ]]; then
  return 0
fi
typeset -g _THEGENT_PLUGIN_LOADED=1

# Determine plugin directory
_THEGENT_PLUGIN_DIR="${${(%):-%x}:h}"
[[ -z "$_THEGENT_PLUGIN_DIR" ]] && _THEGENT_PLUGIN_DIR="$(dirname "$0")"

# --- Source components ---
# Core functions
if [[ -f "$_THEGENT_PLUGIN_DIR/lib/functions.zsh" ]]; then
  source "$_THEGENT_PLUGIN_DIR/lib/functions.zsh"
fi

# Async operations
if [[ -f "$_THEGENT_PLUGIN_DIR/lib/async.zsh" ]]; then
  source "$_THEGENT_PLUGIN_DIR/lib/async.zsh"
fi

# Tab completions
if [[ -f "$_THEGENT_PLUGIN_DIR/lib/completions.zsh" ]]; then
  source "$_THEGENT_PLUGIN_DIR/lib/completions.zsh"
fi

# --- Configuration ---
# thegent executable path
THEGENT_BIN="${THEGENT_BIN:-thegent}"

# Default timeout (seconds)
THEGENT_DEFAULT_TIMEOUT="${THEGENT_DEFAULT_TIMEOUT:-300}"

# Enable/disable async mode
THEGENT_ASYNC_ENABLE="${THEGENT_ASYNC_ENABLE:-1}"

# Work stream file location
THEGENT_WORK_STREAM="${THEGENT_WORK_STREAM:-$HOME/thegent/docs/reference/WORK_STREAM.md}"

# --- Key bindings ---
# Alt+G: Quick thegent prompt
bindkey -s '\eg' 'tg p '

# Alt+F: Quick file agent
bindkey -s '\ef' 'tgf '

# Alt+S: Skills menu
bindkey -s '\es' 'tgs '

# --- Environment ---
export THEGENT_PLUGIN_DIR
export THEGENT_BIN
export THEGENT_DEFAULT_TIMEOUT
export THEGENT_ASYNC_ENABLE
export THEGENT_WORK_STREAM

# --- Completion initialization ---
autoload -Uz compinit
compinit

# --- Status indicator ---
if command -v "$THEGENT_BIN" >/dev/null 2>&1; then
  export THEGENT_AVAILABLE=1
else
  export THEGENT_AVAILABLE=0
  print -r -- "[thegent] Warning: 'thegent' command not found in PATH" >&2
fi
