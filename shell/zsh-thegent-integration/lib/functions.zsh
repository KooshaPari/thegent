# lib/functions.zsh - Helper functions for thegent integration

# --- tg: Quick thegent alias ---
# Usage: tg <command> [args...]
# Examples:
#   tg run "Hello world"
#   tg free --do-next
#   tg ps
#   tg skills
tg() {
  local cmd="${1:-}"
  shift || true

  case "$cmd" in
    run)
      thegent run "$@"
      ;;
    free)
      thegent free "$@"
      ;;
    bg)
      thegent bg "$@"
      ;;
    ps)
      thegent ps "$@"
      ;;
    skills)
      thegent skills "$@"
      ;;
    hooks)
      thegent hooks "$@"
      ;;
    lsp)
      thegent lsp "$@"
      ;;
    mcp)
      thegent mcp "$@"
      ;;
    serve)
      thegent serve "$@"
      ;;
    plan)
      thegent plan "$@"
      ;;
    ""|"help"|"-h"|"--help")
      _tg_usage
      ;;
    *)
      # Forward any unknown command directly to thegent
      command thegent "$cmd" "$@"
      ;;
  esac
}

_tg_usage() {
  print -r -- 'thegent zsh integration

Usage: tg <command> [args...]

Commands:
  run              Execute agent task
  free             Run with free tier (default)
  bg               Background execution
  ps               List active sessions
  skills           List available skills
  hooks            List lifecycle hooks
  lsp              LSP server management
  mcp              MCP server management
  serve            Start MCP server
  plan             Plan management

Shortcuts:
  tg p <prompt>    Quick prompt (same as: tg run "<prompt>")
  tg f <file>      Run agent on file (tgf)
  tg w             Watch mode
  tg s <skill>     Run skill

Examples:
  tg p "Analyze this codebase"
  tg run "Review PR #123"
  tg free --do-next
  tg mcp status
  tg skills list

Key bindings:
  Alt+G - Quick thegent prompt
  Alt+F - Quick file agent
  Alt+S - Skills menu
'
}

# --- tgf: Run agent on file ---
# Usage: tgf <file> [prompt]
# Examples:
#   tgf src/main.py
#   tgf src/main.py "Explain this file"
tgf() {
  local file="${1:-}"

  if [[ -z "$file" ]]; then
    print -r -- "Usage: tgf <file> [prompt]" >&2
    return 1
  fi

  if [[ ! -e "$file" ]]; then
    print -r -- "tgf: no such file: $file" >&2
    return 1
  fi

  local prompt="${2:-Analyze and explain this file}"
  local abs_file="${file:A}"

  thegent run "$prompt on $abs_file"
}

# --- tgw: Watch mode for changes ---
# Usage: tgw [path]
# Watch for file changes and auto-run thegent
tgw() {
  local watch_path="${1:-.}"
  local session_id=""

  if [[ ! -d "$watch_path" ]]; then
    print -r -- "tgw: not a directory: $watch_path" >&2
    return 1
  fi

  # Check for fswatch/entr
  local watcher=""
  if command -v fswatch >/dev/null 2>&1; then
    watcher="fswatch"
  elif command -v entr >/dev/null 2>&1; then
    watcher="entr"
  else
    print -r -- "tgw: requires fswatch or entr" >&2
    print -r -- "Install: brew install fswatch  # or: brew install entr" >&2
    return 1
  fi

  print -r -- "[thegent] Watching $watch_path for changes..."

  case "$watcher" in
    fswatch)
      fswatch -r "$watch_path" | while read -r changed; do
        print -r -- "[thegent] Change detected: $changed"
        # Could trigger agent here
      done
      ;;
    entr)
      find "$watch_path" -type f | entr -d thegent run "File changed in $watch_path"
      ;;
  esac
}

# --- tgs: Run skill ---
# Usage: tgs <skill> [args...]
# Examples:
#   tgs agent-orchestra
#   tgs sitback-agent
#   tgs list
tgs() {
  local skill="${1:-}"

  if [[ -z "$skill" ]]; then
    # List available skills
    thegent skills list
    return $?
  fi

  shift || true
  thegent run --skill "$skill" "$@"
}

# --- tgp: Quick prompt ---
# Usage: tgp <prompt>
# Short for: tg run "<prompt>"
tgp() {
  local prompt="$*"

  if [[ -z "$prompt" ]]; then
    print -r -- "Usage: tgp <prompt>" >&2
    print -r -- "Example: tgp Analyze this codebase" >&2
    return 1
  fi

  thegent run "$prompt"
}

# --- tgwho: Who am I in thegent ---
# Show current agent context
tgwho() {
  local agent_id="${AGENT_ID:-}"
  local session_id="${THEGENT_SESSION_ID:-}"
  local work_dir="${THEGENT_WORK_DIR:-$(pwd)}"

  print -r -- "thegent context:"
  print -r -- "  Agent ID: ${agent_id:-<none>}"
  print -r -- "  Session: ${session_id:-<none>}"
  print -r -- "  Work dir: $work_dir"

  if command -v thegent >/dev/null 2>&1; then
    local status
    status=$(thegent ps 2>/dev/null | head -20)
    if [[ -n "$status" ]]; then
      print -r -- ""
      print -r -- "Active sessions:"
      print -r -- "$status"
    fi
  fi
}

# --- tgwork: Show work stream ---
# Display current work stream items
tgwork() {
  local stream_file="${THEGENT_WORK_STREAM:-$HOME/thegent/docs/reference/WORK_STREAM.md}"

  if [[ -f "$stream_file" ]]; then
    print -r -- "Work stream from: $stream_file"
    print -r -- ""
    head -100 "$stream_file"
  else
    print -r -- "tgwork: work stream not found: $stream_file" >&2
    print -r -- "Set THEGENT_WORK_STREAM to customize location" >&2
  fi
}

# --- tgnext: Get next item from work stream ---
tgnext() {
  if command -v thegent >/dev/null 2>&1; then
    thegent plan do-next "$@"
  else
    print -r -- "tgnext: thegent not found" >&2
    return 1
  fi
}

# --- tgmcp: Quick MCP commands ---
tgmcp() {
  local cmd="${1:-status}"

  case "$cmd" in
    up)
      thegent mcp up "$@"
      ;;
    down)
      thegent mcp down "$@"
      ;;
    status)
      thegent mcp status "$@"
      ;;
    prune)
      thegent mcp prune "$@"
      ;;
    *)
      thegent mcp "$@"
      ;;
  esac
}

# --- tglog: View thegent logs ---
# Usage: tglog [lines]
tglog() {
  local lines="${1:-50}"
  local log_file="${THEGENT_LOG_FILE:-$HOME/.thegent/logs/thegent.log}"

  if [[ -f "$log_file" ]]; then
    tail -n "$lines" "$log_file"
  else
    # Try alternative locations
    if [[ -f "$HOME/thegent/swarm.log" ]]; then
      tail -n "$lines" "$HOME/thegent/swarm.log"
    else
      print -r -- "tglog: no log file found" >&2
      return 1
    fi
  fi
}

# --- tgstatus: Quick status check ---
tgstatus() {
  echo "=== thegent Status ==="

  # Check if thegent is available
  if command -v thegent >/dev/null 2>&1; then
    echo "✓ thegent: available"
    thegent --version 2>/dev/null || echo "  (version unknown)"
  else
    echo "✗ thegent: NOT FOUND in PATH"
  fi

  # Check MCP server
  if command -v thegent >/dev/null 2>&1; then
    local mcp_status
    mcp_status=$(thegent mcp status 2>&1)
    if echo "$mcp_status" | grep -q "running"; then
      echo "✓ MCP server: running"
    else
      echo "○ MCP server: not running"
      echo "  Run: thegent mcp up"
    fi
  fi

  # Show active sessions
  if command -v thegent >/dev/null 2>&1; then
    local sessions
    sessions=$(thegent ps 2>/dev/null)
    if [[ -n "$sessions" ]]; then
      echo ""
      echo "Active sessions:"
      echo "$sessions" | head -10
    fi
  fi

  echo ""
  echo "Variables:"
  echo "  THEGENT_WORK_STREAM=$THEGENT_WORK_STREAM"
  echo "  THEGENT_LOG_FILE=$THEGENT_LOG_FILE"
  echo "  THEGENT_ASYNC_ENABLE=$THEGENT_ASYNC_ENABLE"
}

# --- tgdoc: Open thegent docs ---
tgdoc() {
  local topic="${1:-}"
  local docs_dir="$HOME/thegent/docs"

  if [[ -d "$docs_dir" ]]; then
    if [[ -z "$topic" ]]; then
      ls "$docs_dir"
    else
      local found
      found=$(find "$docs_dir" -iname "*${topic}*" -type f 2>/dev/null | head -5)
      if [[ -n "$found" ]]; then
        echo "$found"
      else
        print -r -- "tgdoc: no docs found for: $topic" >&2
      fi
    fi
  else
    print -r -- "tgdoc: docs not found at: $docs_dir" >&2
  fi
}
