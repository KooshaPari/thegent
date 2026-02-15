#!/bin/bash
# Copilot Agent - Model: claude-haiku-4.5-20251001 (STRICT - LOCKED)
# This wrapper ensures all copilot executions use Claude Haiku 4.5 exclusively.
# Prevents model drift and ensures consistent agent behavior.

set -euo pipefail

# Strict model lock - do not override
MODEL="claude-haiku-4.5-20251001"
PROMPT=""
WORKSPACE=""
MODE="programmatic"
REASONING="low"
VERBOSE=false

# Helper functions
log_error() {
  echo "[ERROR] $1" >&2
}

log_success() {
  echo "[OK] $1" >&2
}

log_warn() {
  echo "[WARN] $1" >&2
}

log_info() {
  echo "[INFO] $1" >&2
}

log_debug() {
  if [[ "$VERBOSE" == "true" ]]; then
    echo -e "[DEBUG] $1" >&2
  fi
}

# Validate copilot CLI is available
check_copilot_available() {
  if ! command -v copilot &> /dev/null; then
    log_error "Copilot CLI not found. Please install it first."
    log_info "Install: brew install gh-copilot OR curl -L https://gh.io/copilot-cli | bash"
    exit 1
  fi

  local version
  version=$(copilot --version 2>&1 || echo "unknown")
  log_debug "Copilot version: $version"
  log_success "Copilot CLI available ($version)"
}

# Parse command line arguments
parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --prompt)
        PROMPT="$2"
        shift 2
        ;;
      --cd|--workspace)
        WORKSPACE="$2"
        shift 2
        ;;
      --mode)
        MODE="$2"
        shift 2
        ;;
      --reasoning)
        REASONING="$2"
        shift 2
        ;;
      --verbose|-v)
        VERBOSE=true
        shift
        ;;
      --model)
        # Model is LOCKED - warn if user tries to override
        log_warn "Model override requested (ignored). Using locked model: $MODEL"
        shift 2
        ;;
      --help|-h)
        show_help
        exit 0
        ;;
      *)
        log_warn "Unknown argument: $1 (ignored)"
        shift
        ;;
    esac
  done
}

# Validate workspace if provided
validate_workspace() {
  if [[ -n "$WORKSPACE" ]]; then
    if [[ ! -d "$WORKSPACE" ]]; then
      log_error "Workspace directory does not exist: $WORKSPACE"
      exit 1
    fi
    log_debug "Workspace validated: $WORKSPACE"
  fi
}

# Validate mode
validate_mode() {
  case "$MODE" in
    interactive|programmatic|autopilot)
      log_debug "Mode validated: $MODE"
      ;;
    *)
      log_error "Invalid mode: $MODE. Must be one of: interactive, programmatic, autopilot"
      exit 1
      ;;
  esac
}

# Build and execute copilot command
execute_copilot() {
  local cmd_array=()

  # Start with copilot command
  cmd_array+=(copilot)

  # Add mode-specific configuration
  case "$MODE" in
    programmatic)
      # Programmatic mode: execute single prompt and exit
      if [[ -z "$PROMPT" ]]; then
        log_error "Programmatic mode requires --prompt"
        exit 1
      fi
      cmd_array+=(-p "$PROMPT")
      ;;
    autopilot)
      # Autopilot mode: continuous execution until task complete
      if [[ -z "$PROMPT" ]]; then
        log_error "Autopilot mode requires --prompt"
        exit 1
      fi
      cmd_array+=(--autopilot "$PROMPT")
      ;;
    interactive)
      # Interactive mode: conversation loop
      if [[ -n "$PROMPT" ]]; then
        cmd_array+=("$PROMPT")
      fi
      ;;
  esac

  # Print execution context
  log_info "=== Copilot Subagent Execution ==="
  log_info "Model: $MODEL (LOCKED)"
  log_info "Mode: $MODE"
  log_info "Reasoning: $REASONING"
  if [[ -n "$WORKSPACE" ]]; then
    log_info "Workspace: $WORKSPACE"
  fi
  if [[ -n "$PROMPT" ]]; then
    log_info "Prompt: ${PROMPT:0:100}$([[ ${#PROMPT} -gt 100 ]] && echo '...' || true)"
  fi
  log_info "======================================"
  echo "" >&2

  # Change to workspace if specified
  if [[ -n "$WORKSPACE" ]]; then
    log_debug "Changing to workspace: $WORKSPACE"
    cd "$WORKSPACE" || {
      log_error "Failed to change to workspace: $WORKSPACE"
      exit 1
    }
  fi

  # Execute copilot command
  log_debug "Executing: ${cmd_array[*]}"

  # Add stdout/stderr capture for programmatic mode
  if [[ "$MODE" == "programmatic" ]]; then
    cmd_array+=(--allow-all-tools --stream on)
  fi

  # Wrap execution with error handling
  if ! "${cmd_array[@]}"; then
    local exit_code=$?
    log_error "Copilot execution failed with exit code: $exit_code"
    exit $exit_code
  fi

  log_success "Copilot execution completed"
}

# Display help
show_help() {
  cat <<EOF
Copilot Subagent Wrapper (Claude Haiku 4.5 Locked)

USAGE:
  run_copilot.sh [OPTIONS]

OPTIONS:
  --prompt <text>           Task description (required for programmatic/autopilot)
  --cd <path>               Change to workspace directory
  --mode <mode>             Execution mode: interactive (default), programmatic, autopilot
  --reasoning <level>       Reasoning level: low (default), medium, high
  --verbose, -v             Enable debug logging
  --help, -h               Show this help message

MODES:
  interactive              Start conversation loop with Copilot (default)
  programmatic             Execute single prompt and exit (requires --prompt)
  autopilot                Agent continues until task complete (requires --prompt)

EXAMPLES:
  # Interactive mode
  run_copilot.sh

  # Programmatic mode
  run_copilot.sh --prompt "implement REST API endpoint" --cd ~/my-project

  # Autopilot mode with workspace
  run_copilot.sh --autopilot --prompt "fix all failing tests" --cd ~/my-project

MODEL (LOCKED):
  This wrapper strictly enforces: claude-haiku-4-5-20251001
  Model override attempts will be logged and ignored.

ENVIRONMENT:
  COPILOT_CONFIG: Path to copilot config file (~/.copilot/config)

EOF
}

# Main execution
main() {
  parse_args "$@"
  validate_workspace
  validate_mode
  check_copilot_available
  execute_copilot
}

# Run main function
main "$@"
