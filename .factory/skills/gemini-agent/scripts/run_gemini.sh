#!/bin/bash
# Gemini Agent - Uses default gemini-cli model (configured in ~/.gemini/config.json)
# Note: Model override not working - gemini-3-flash not found. Using default.
PROMPT=""
WORKSPACE=""
MODE="default"

show_help() {
  cat <<EOF
Gemini Agent Wrapper (1M+ token context)

USAGE:
  run_gemini.sh [OPTIONS]

OPTIONS:
  --prompt <text>          Task description
  --cd <path>              Change to workspace directory
  --mode <mode>            Execution mode: read-only, workspace-write, danger-full-access
  --model <model>          Model selection (ignored - uses ~/.gemini/config.json)
  --help, -h               Show this help message

MODES:
  read-only                Analysis without modifications (security scans, audits)
  workspace-write          Autonomous file editing (--approval-mode auto_edit)
  danger-full-access       Full system access (--approval-mode yolo)

EXAMPLES:
  # Security scan (read-only)
  run_gemini.sh --prompt "Scan for OWASP vulnerabilities" --mode read-only

  # Code refactoring
  run_gemini.sh --prompt "Refactor auth module" --mode workspace-write --cd ~/my-project

  # Full repo analysis
  run_gemini.sh --prompt "Analyze entire codebase architecture" --cd ~/my-project

CAPABILITIES:
  - 1M+ token context window (entire repositories)
  - Multi-modal understanding (code + images + docs)
  - Security scanning (OWASP, secrets, SBOM)
  - Large-scale transformations and migrations

MODEL:
  Uses model configured in ~/.gemini/config.json
  Default: Gemini 2.5 Pro or Gemini 2.5 Flash
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h) show_help ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --cd) WORKSPACE="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --model) shift 2 ;; # Ignore model for now (not working)
    *) shift ;;
  esac
done

# Change to workspace if specified
if [[ -n "$WORKSPACE" ]]; then
  cd "$WORKSPACE" 2>/dev/null || true
fi

# Build gemini command
CMD=(gemini)

# Map mode to gemini's approval-mode
# Note: plan mode requires experimental.plan config - skip for read-only
case "$MODE" in
  read-only|plan)
    # Plan mode requires experimental flag - fall back to default with prompt
    ;;
  workspace-write)
    CMD+=(--approval-mode auto_edit)
    ;;
  danger-full-access)
    CMD+=(--approval-mode yolo)
    ;;
esac

# Add output format flag (JSON for structured output)
CMD+=(--output-format text)

# Add prompt
if [[ -n "$PROMPT" ]]; then
  CMD+=(--prompt "$PROMPT")
fi

# Suppress Node deprecation warnings (e.g. punycode)
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--no-deprecation"

# Execute gemini with output capture
"${CMD[@]}"
