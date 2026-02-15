#!/bin/bash
# Cursor Agent - Model: gemini-3-flash (STRICT)
# Note: Cursor agent doesn't support model override - uses configured model
MODEL="gemini-3-flash"
PROMPT=""
WORKSPACE=""
MODE=""
TIMEOUT=300

show_help() {
  cat <<EOF
Cursor Agent Wrapper (Model: gemini-3-flash)

USAGE:
  run_cursor.sh [OPTIONS]

OPTIONS:
  --prompt <text>          Task description (required for non-interactive mode)
  --cd <path>              Change to workspace directory
  --mode <mode>            Execution mode: plan, ask, workspace-write, danger-full-access
  --help, -h               Show this help message

MODES:
  plan                     Design approach before implementation
  ask                      Interactive Q&A mode
  workspace-write          Autonomous file editing (default)
  danger-full-access       Full system access

EXAMPLES:
  # Plan mode
  run_cursor.sh --prompt "Design authentication system" --mode plan

  # Interactive mode
  run_cursor.sh --prompt "Implement REST API" --cd ~/my-project

  # Workspace write mode
  run_cursor.sh --prompt "Refactor handlers" --mode workspace-write

MODEL:
  Uses Cursor's configured model (gemini-3-flash)
  Model override not supported by Cursor CLI
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h) show_help ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --cd) WORKSPACE="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Change to workspace if specified
if [[ -n "$WORKSPACE" ]]; then
  cd "$WORKSPACE" 2>/dev/null || true
fi

# Require prompt for print mode
if [[ -z "$PROMPT" ]]; then
  echo "Error: No prompt provided for print mode" >&2
  echo "Use --help for usage information" >&2
  exit 1
fi

# Build cursor command with agent mode for output capture
CMD=(cursor agent)

# Use --print for non-interactive output; --trust to skip workspace approval prompt
CMD+=(--print --trust)

# Map mode to cursor's mode option (only plan and ask are supported)
if [[ -n "$MODE" ]]; then
  case "$MODE" in
    read-only|plan)
      CMD+=(--mode plan)
      ;;
    ask)
      CMD+=(--mode ask)
      ;;
    workspace-write|danger-full-access)
      # Default mode (no flag) allows writes
      ;;
  esac
fi

# Add workspace explicitly (cursor needs it for headless)
if [[ -n "$WORKSPACE" ]]; then
  CMD+=(--workspace "$WORKSPACE")
fi

# Add prompt
if [[ -n "$PROMPT" ]]; then
  CMD+=("$PROMPT")
fi

# Execute cursor agent with output (stdin from /dev/null for non-interactive)
timeout "$TIMEOUT" "${CMD[@]}" < /dev/null
EXIT_CODE=$?
if [[ $EXIT_CODE -eq 124 ]]; then
  echo "Error: Cursor agent timed out after ${TIMEOUT}s" >&2
  exit 124
fi
exit $EXIT_CODE
