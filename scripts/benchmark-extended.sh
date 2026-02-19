#!/usr/bin/env bash
# Extended benchmark suite for hook-rust migration analysis
# Includes operation-level, hook-level, and aggregate benchmarks
# Usage: bash scripts/benchmark-extended.sh [OPTIONS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_ROOT="${THEGENT_BENCH_RESULTS_DIR:-$THEGENT_ROOT/benchmarks/results}"

export LC_ALL=C
export TZ=UTC

# Configuration
WARMUP_RUNS="${BENCH_WARMUP_RUNS:-3}"
MEASURE_RUNS="${BENCH_MEASURE_RUNS:-20}"
DRY_RUN="${BENCH_DRY_RUN:-0}"
VERBOSE="${BENCH_VERBOSE:-0}"

# Scenario mode
SCENARIO="${BENCH_SCENARIO:-all}"  # all | operations | hooks | aggregate

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utilities
log_info() {
  echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
  echo -e "${GREEN}[OK]${NC} $*" >&2
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Check dependencies
check_deps() {
  local deps=("hyperfine" "python3" "jq")
  for cmd in "${deps[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      log_error "missing required dependency: $cmd"
      exit 1
    fi
  done
  log_success "all dependencies available"
}

# Setup benchmark environment
setup_benchmark() {
  RUN_SHA="$(git -C "$THEGENT_ROOT" rev-parse --short HEAD 2>/dev/null || echo no-git)"
  RUN_STAMP="${BENCH_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$RUN_SHA}"
  RUN_DIR="$RESULTS_ROOT/$RUN_STAMP"
  BASELINE_DIR="$RUN_DIR/baseline"
  CURRENT_DIR="$RUN_DIR/current"
  REPORT_PATH="$RUN_DIR/report.md"
  SUMMARY_PATH="$RUN_DIR/summary.json"
  MANIFEST_PATH="$RUN_DIR/manifest.json"

  mkdir -p "$BASELINE_DIR" "$CURRENT_DIR"

  log_info "Benchmark environment:"
  log_info "  Run ID:        $RUN_STAMP"
  log_info "  Results dir:   $RUN_DIR"
  log_info "  Warmup runs:   $WARMUP_RUNS"
  log_info "  Measure runs:  $MEASURE_RUNS"
  log_info "  Scenario:      $SCENARIO"
  log_info "  Dry run:       $DRY_RUN"
}

# Run single hyperfine benchmark
run_hyperfine() {
  local label="$1"
  local output_path="$2"
  local command="$3"

  echo "  - $label"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "    [dry-run] hyperfine --warmup $WARMUP_RUNS --runs $MEASURE_RUNS --export-json $output_path '$command'"
    return 0
  fi

  hyperfine \
    --warmup "$WARMUP_RUNS" \
    --runs "$MEASURE_RUNS" \
    --export-json "$output_path" \
    "$command" \
    >/dev/null 2>&1 || {
    log_warn "benchmark failed: $label"
    return 1
  }
}

# Run operation-level benchmarks
benchmark_operations() {
  log_info "Running operation-level benchmarks..."

  echo "Scenario: hook_init"
  run_hyperfine \
    "baseline/bash" \
    "$BASELINE_DIR/01_hook_init_bash.json" \
    "bash -lc 'source \"$THEGENT_ROOT/hooks/lib/common.sh\" 2>/dev/null; hook_init_full 2>/dev/null || echo init_done'"

  if command -v thegent-hooks >/dev/null 2>&1; then
    run_hyperfine \
      "current/rust" \
      "$CURRENT_DIR/01_hook_init_rust.json" \
      "echo '{\"hook_name\":\"test\",\"project_dir\":\".\"}' | thegent-hooks init 2>/dev/null || true"
  else
    log_warn "thegent-hooks not found, skipping rust benchmark"
  fi

  echo ""
  echo "Scenario: cache_key"
  run_hyperfine \
    "baseline/bash" \
    "$BASELINE_DIR/02_cache_key_bash.json" \
    "bash -lc 'source \"$THEGENT_ROOT/hooks/lib/common.sh\" 2>/dev/null; hook_cache_key \"test\" \"abc123\" \"file1.rs file2.rs\" 2>/dev/null || echo key'"

  if command -v thegent-hooks >/dev/null 2>&1; then
    run_hyperfine \
      "current/rust" \
      "$CURRENT_DIR/02_cache_key_rust.json" \
      "thegent-hooks cache-key \"test\" \"abc123\" \"file1.rs\" \"file2.rs\" 2>/dev/null || true"
  fi

  echo ""
  echo "Scenario: tool_detection"
  run_hyperfine \
    "baseline/bash" \
    "$BASELINE_DIR/03_tool_detection_bash.json" \
    "bash -lc 'command -v jq >/dev/null 2>&1 && command -v rg >/dev/null 2>&1 && command -v fd >/dev/null 2>&1 && echo ok'"

  if command -v thegent-tool-detect >/dev/null 2>&1; then
    run_hyperfine \
      "current/rust" \
      "$CURRENT_DIR/03_tool_detection_rust.json" \
      "thegent-tool-detect --json 2>/dev/null | jq .jq 2>/dev/null >/dev/null || true"
  fi

  echo ""
  echo "Scenario: path_resolution"
  run_hyperfine \
    "baseline/bash" \
    "$BASELINE_DIR/04_path_resolution_bash.json" \
    "bash -lc 'for dir in \${PATH//:/ }; do if [[ -x \"\$dir/git\" ]]; then echo \"\$dir/git\"; break; fi; done'"

  if command -v thegent-path-resolve >/dev/null 2>&1; then
    run_hyperfine \
      "current/rust" \
      "$CURRENT_DIR/04_path_resolution_rust.json" \
      "thegent-path-resolve git 2>/dev/null || true"
  fi

  echo ""
  echo "Scenario: git_status"
  run_hyperfine \
    "baseline/git" \
    "$BASELINE_DIR/05_git_status_bash.json" \
    "git -C \"$THEGENT_ROOT\" status --short"

  if command -v thegent-hooks >/dev/null 2>&1; then
    run_hyperfine \
      "current/thegent-hooks" \
      "$CURRENT_DIR/05_git_status_rust.json" \
      "cd \"$THEGENT_ROOT\" && thegent-hooks git status --short 2>/dev/null || true"
  fi

  echo ""
  echo "Scenario: changed_files"
  run_hyperfine \
    "baseline/git" \
    "$BASELINE_DIR/06_changed_files_bash.json" \
    "git -C \"$THEGENT_ROOT\" diff --name-only HEAD~1..HEAD 2>/dev/null || git -C \"$THEGENT_ROOT\" diff --name-only"

  if command -v thegent-hooks >/dev/null 2>&1; then
    run_hyperfine \
      "current/thegent-hooks" \
      "$CURRENT_DIR/06_changed_files_rust.json" \
      "cd \"$THEGENT_ROOT\" && thegent-hooks changed-files 2>/dev/null | wc -l || true"
  fi
}

# Run hook-level benchmarks
benchmark_hooks() {
  log_info "Running hook-level benchmarks..."

  # Find some actual hooks
  local hooks=(
    "pre-write-validator.sh"
    "doc-location-guard.sh"
    "friction-detector.sh"
  )

  for hook in "${hooks[@]}"; do
    local hook_path="$THEGENT_ROOT/hooks/$hook"
    if [[ -f "$hook_path" ]]; then
      echo ""
      echo "Hook: $hook"
      run_hyperfine \
        "baseline/bash" \
        "$BASELINE_DIR/hook_${hook%.sh}_bash.json" \
        "bash \"$hook_path\" <<< '{}' 2>/dev/null || true"
    fi
  done
}

# Run aggregate benchmarks
benchmark_aggregate() {
  log_info "Running aggregate benchmarks..."

  # Simulate 10 sequential hook invocations
  echo ""
  echo "Scenario: sequential_hooks (10x)"
  run_hyperfine \
    "baseline/sequential" \
    "$BASELINE_DIR/10_sequential_hooks_bash.json" \
    "for i in {1..10}; do bash -lc 'source \"$THEGENT_ROOT/hooks/lib/common.sh\" 2>/dev/null; hook_init_full 2>/dev/null' || true; done"

  if command -v thegent-hooks >/dev/null 2>&1; then
    run_hyperfine \
      "current/sequential" \
      "$CURRENT_DIR/10_sequential_hooks_rust.json" \
      "for i in {1..10}; do echo '{\"hook_name\":\"test\",\"project_dir\":\".\"}' | thegent-hooks init >/dev/null 2>&1 || true; done"
  fi
}

# Generate analysis report
generate_report() {
  log_info "Generating analysis report..."

  if [[ "$DRY_RUN" == "1" ]]; then
    cat >"$REPORT_PATH" <<'EOF'
# Hook Rust Benchmark Report (Dry Run)

This is a dry run. No actual benchmarks were executed.

Run without `BENCH_DRY_RUN=1` to execute real benchmarks.
EOF
    cat >"$SUMMARY_PATH" <<EOF
{"dry_run": true, "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
    return
  fi

  # Generate markdown report
  python3 "$THEGENT_ROOT/scripts/benchmark-report.py" \
    --baseline-dir "$BASELINE_DIR" \
    --current-dir "$CURRENT_DIR" \
    --report-path "$REPORT_PATH" \
    --summary-path "$SUMMARY_PATH" \
    --title "Hook Rust Benchmark Comparison (Extended)"
}

# Save manifest
save_manifest() {
  cat >"$MANIFEST_PATH" <<EOF
{
  "run_id": "$RUN_STAMP",
  "generated_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_sha": "$RUN_SHA",
  "scenario": "$SCENARIO",
  "warmup_runs": $WARMUP_RUNS,
  "measure_runs": $MEASURE_RUNS,
  "dry_run": $DRY_RUN,
  "baseline_dir": "$BASELINE_DIR",
  "current_dir": "$CURRENT_DIR",
  "uname": "$(uname -a)",
  "git_version": "$(git --version)",
  "bash_version": "$(bash --version | head -1)"
}
EOF
}

# Display usage
usage() {
  cat <<EOF
Hook Rust Migration - Extended Benchmark Suite

Usage: bash $(basename "$0") [OPTIONS]

Options:
  --scenario SCENARIO   Benchmark scenario (all|operations|hooks|aggregate)
                        Default: all
  --warmup N            Warmup runs (default: $WARMUP_RUNS)
  --runs N              Measurement runs (default: $MEASURE_RUNS)
  --dry-run             Plan only, don't execute benchmarks
  --verbose             Verbose output
  --help                Show this help message

Environment Variables:
  THEGENT_BENCH_RESULTS_DIR  Results directory (default: benchmarks/results)
  BENCH_RUN_ID               Custom run ID (default: timestamp-sha)
  BENCH_WARMUP_RUNS          Warmup runs (default: 3)
  BENCH_MEASURE_RUNS         Measurement runs (default: 20)
  BENCH_DRY_RUN              Dry run mode (0|1, default: 0)
  BENCH_SCENARIO             Benchmark scenario (default: all)
  BENCH_VERBOSE              Verbose output (0|1, default: 0)

Examples:
  # Run all benchmarks with defaults
  bash scripts/benchmark-extended.sh

  # Dry run to see what would execute
  BENCH_DRY_RUN=1 bash scripts/benchmark-extended.sh

  # Run only operation-level benchmarks
  BENCH_SCENARIO=operations bash scripts/benchmark-extended.sh

  # Run with custom settings
  BENCH_WARMUP_RUNS=5 BENCH_MEASURE_RUNS=30 bash scripts/benchmark-extended.sh

EOF
  exit "${1:-0}"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --scenario)
    SCENARIO="$2"
    shift 2
    ;;
  --warmup)
    WARMUP_RUNS="$2"
    shift 2
    ;;
  --runs)
    MEASURE_RUNS="$2"
    shift 2
    ;;
  --dry-run)
    DRY_RUN=1
    shift
    ;;
  --verbose)
    VERBOSE=1
    shift
    ;;
  --help)
    usage 0
    ;;
  *)
    log_error "unknown option: $1"
    usage 1
    ;;
  esac
done

# Main execution
main() {
  log_info "Hook Rust Benchmark Suite (Extended)"

  check_deps
  setup_benchmark

  # Run selected scenarios
  case "$SCENARIO" in
  all)
    benchmark_operations
    benchmark_hooks
    benchmark_aggregate
    ;;
  operations)
    benchmark_operations
    ;;
  hooks)
    benchmark_hooks
    ;;
  aggregate)
    benchmark_aggregate
    ;;
  *)
    log_error "unknown scenario: $SCENARIO"
    exit 1
    ;;
  esac

  # Generate outputs
  generate_report
  save_manifest
  ln -sfn "$RUN_STAMP" "$RESULTS_ROOT/latest"

  # Summary
  echo ""
  log_success "Benchmarking complete"
  echo ""
  log_info "Results:"
  echo "  Run directory: $RUN_DIR"
  echo "  Manifest:      $MANIFEST_PATH"
  echo "  Report:        $REPORT_PATH"
  echo "  Summary JSON:  $SUMMARY_PATH"
  echo ""

  if [[ "$DRY_RUN" != "1" ]]; then
    # Print quick summary
    if [[ -f "$SUMMARY_PATH" ]]; then
      log_success "Quick summary:"
      python3 -c "
import json
try:
    with open('$SUMMARY_PATH') as f:
        data = json.load(f)
        if 'results' in data:
            for result in data['results'][:5]:
                ratio = result.get('ratio', 1.0)
                status = '✅' if ratio > 1 else '⚠️'
                print(f'  {status} {result[\"name\"]}: {ratio:.1f}x')
except: pass
      " || true
    fi
  fi
}

main
