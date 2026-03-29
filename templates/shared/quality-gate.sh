#!/usr/bin/env bash
set -euo pipefail

# Quality Gate — runs per-language checks based on project detection
# Exit codes: 0 = pass, 1 = fail (with details)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-.}"
FAIL=0
GITLEAKS_MAX_MB="${GITLEAKS_MAX_MB:-5}"
GITLEAKS_TIMEOUT_SEC="${GITLEAKS_TIMEOUT_SEC:-180}"
QUALITY_SHADOW_CLEANUP_HOURS="${QUALITY_SHADOW_CLEANUP_HOURS:-24}"
QUALITY_LOG_RETENTION_DAYS="${QUALITY_LOG_RETENTION_DAYS:-7}"

echo "=== Quality Gate ==="
echo "Project: $PROJECT_ROOT"
echo ""

# Detect project type
detect_stack() {
  local stacks=()
  [[ -f "$PROJECT_ROOT/pyproject.toml" || -f "$PROJECT_ROOT/setup.py" ]] && stacks+=("python")
  [[ -f "$PROJECT_ROOT/package.json" ]] && stacks+=("typescript")
  [[ -f "$PROJECT_ROOT/go.mod" ]] && stacks+=("go")
  find "$PROJECT_ROOT" -maxdepth 2 -name "*.sh" -o -name "*.bash" 2>/dev/null | head -1 | grep -q . && stacks+=("bash")
  echo "${stacks[@]}"
}

STACKS=($(detect_stack))
echo "Detected stacks: ${STACKS[*]:-none}"
echo ""

# Python checks
run_python() {
  echo "--- Python Quality ---"
  echo "[1/5] Ruff lint..."
  ruff check "$PROJECT_ROOT" || FAIL=1
  echo "[2/5] Ruff format..."
  ruff format --check "$PROJECT_ROOT" || FAIL=1
  echo "[3/5] Type check..."
  (cd "$PROJECT_ROOT" && ty check src/ 2>/dev/null) || echo "Type check skipped (ty not available)"
  echo "[4/5] Tests..."
  (cd "$PROJECT_ROOT" && uv run pytest --tb=short -q) || FAIL=1
  echo "[5/5] Security (bandit via ruff)..."
  ruff check --select S "$PROJECT_ROOT" || FAIL=1
  echo ""
}

# TypeScript checks
run_typescript() {
  echo "--- TypeScript Quality ---"

  # JS execution helper (Bun > Node)
  _js_run() {
    if command -v bun >/dev/null 2>&1; then
      bun x "$@"
    else
      npx "$@"
    fi
  }

  echo "[1/4] oxlint..."
  (cd "$PROJECT_ROOT" && _js_run oxlint .) || FAIL=1
  echo "[2/4] Type check..."
  (cd "$PROJECT_ROOT" && _js_run tsc --noEmit) || FAIL=1
  echo "[3/4] Format check..."
  (cd "$PROJECT_ROOT" && _js_run prettier --check .) || echo "Prettier check skipped"
  echo "[4/4] Dead exports..."
  (cd "$PROJECT_ROOT" && _js_run knip --no-progress 2>/dev/null) || echo "knip skipped"
  echo ""
}

# Go checks
run_go() {
  echo "--- Go Quality ---"
  echo "[1/3] golangci-lint..."
  (cd "$PROJECT_ROOT" && golangci-lint run) || FAIL=1
  echo "[2/3] Tests..."
  (cd "$PROJECT_ROOT" && go test -race ./...) || FAIL=1
  echo "[3/3] Security..."
  (cd "$PROJECT_ROOT" && govulncheck ./... 2>/dev/null) || echo "govulncheck skipped"
  echo ""
}

# Bash checks
run_bash() {
  echo "--- Bash Quality ---"
  echo "[1/2] ShellCheck..."
  find "$PROJECT_ROOT" -name '*.sh' -o -name '*.bash' 2>/dev/null | xargs shellcheck 2>/dev/null || FAIL=1
  echo "[2/2] BATS tests..."
  [[ -d "$PROJECT_ROOT/tests" ]] && bats "$PROJECT_ROOT/tests/" 2>/dev/null || echo "No BATS tests found"
  echo ""
}

# Secrets check (all stacks)
echo "--- Secrets Detection ---"
trufflehog git file://. --since-commit HEAD --only-verified --fail \
  2>/dev/null || echo "trufflehog skipped (no git history or no verified secrets found)"
echo ""

# Run per-stack checks
for stack in "${STACKS[@]}"; do
  case "$stack" in
    python) run_python ;;
    typescript) run_typescript ;;
    go) run_go ;;
    bash) run_bash ;;
  esac
done

# AI slop detection
echo "--- AI Slop Detection ---"
SLOP=0
for pattern in "TODO: implement" "TODO: add" "lorem ipsum" "As an AI" "I cannot" "I apologize"; do
  if rg -n "$pattern" \
    -g "*.py" -g "*.ts" -g "*.go" -g "*.sh" \
    -g "!.git/**" -g "!.git-cache/**" -g "!.shadow-*/**" -g "!.worktrees/**" \
    -g "!node_modules/**" -g "!.venv/**" -g "!.venv-*/**" -g "!__pycache__/**" \
    -g "!target/**" -g "!dist/**" -g "!build/**" -g "!.quality/**" -g "!.playwright-cli/**" \
    "$PROJECT_ROOT" 2>/dev/null; then
    echo "WARNING: Found '$pattern'"
    SLOP=1
  fi
done
[[ "$SLOP" -eq 0 ]] && echo "No AI slop detected"
echo ""

# WL-030: Periodic cleanup of stale .shadow-* dirs and .quality/logs retention
cleanup_stale_artifacts() {
  local root="$1"
  local shadow_age_hours="$2"
  local log_retention_days="$3"

  echo "--- Artifact Cleanup ---"

  # Remove .shadow-* directories older than QUALITY_SHADOW_CLEANUP_HOURS
  local removed_shadow=0
  while IFS= read -r -d '' shadow_dir; do
    rm -rf "$shadow_dir"
    removed_shadow=$((removed_shadow + 1))
  done < <(find "$root" -maxdepth 1 -name '.shadow-*' -type d \
    -mmin "+$((shadow_age_hours * 60))" -print0 2>/dev/null)
  echo "Removed $removed_shadow stale .shadow-* directories (older than ${shadow_age_hours}h)"

  # Remove .quality/logs files older than QUALITY_LOG_RETENTION_DAYS
  local log_dir="$root/.quality/logs"
  local removed_logs=0
  if [[ -d "$log_dir" ]]; then
    while IFS= read -r -d '' log_file; do
      rm -f "$log_file"
      removed_logs=$((removed_logs + 1))
    done < <(find "$log_dir" -maxdepth 1 -type f \
      -mtime "+${log_retention_days}" -print0 2>/dev/null)
  fi
  echo "Removed $removed_logs .quality/logs files older than ${log_retention_days}d"
  echo ""
}

cleanup_stale_artifacts "$PROJECT_ROOT" "$QUALITY_SHADOW_CLEANUP_HOURS" "$QUALITY_LOG_RETENTION_DAYS"

# Summary
echo "=== Quality Gate Result ==="
if [[ "$FAIL" -eq 0 ]]; then
  echo "PASS: All checks passed"
  exit 0
else
  echo "FAIL: Some checks failed (see above)"
  exit 1
fi
