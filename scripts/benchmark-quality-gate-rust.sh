#!/usr/bin/env zsh
# WL-007.4: Benchmark Rust quality/security binaries vs shell equivalents.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_ROOT="${THEGENT_BENCH_RESULTS_DIR:-$THEGENT_ROOT/benchmarks/results}"
WARMUP_RUNS="${BENCH_WARMUP_RUNS:-3}"
MEASURE_RUNS="${BENCH_MEASURE_RUNS:-20}"
DRY_RUN="${BENCH_DRY_RUN:-0}"

if ! command -v hyperfine >/dev/null 2>&1; then
  echo "benchmark-quality-gate-rust: missing dependency hyperfine" >&2
  echo "Install with: brew install hyperfine  # or cargo install hyperfine" >&2
  exit 1
fi

RUN_SHA="$(git -C "$THEGENT_ROOT" rev-parse --short HEAD 2>/dev/null || echo no-git)"
RUN_STAMP="${BENCH_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$RUN_SHA}"
RUN_DIR="$RESULTS_ROOT/$RUN_STAMP"
BASELINE_DIR="$RUN_DIR/baseline"
CURRENT_DIR="$RUN_DIR/current"
REPORT_PATH="$RUN_DIR/report.md"
SUMMARY_PATH="$RUN_DIR/summary.json"

mkdir -p "$BASELINE_DIR" "$CURRENT_DIR"

run_hyperfine() {
  local label="$1"
  local output_path="$2"
  local command="$3"
  echo "  - $label"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "    [dry-run] hyperfine --warmup $WARMUP_RUNS --runs $MEASURE_RUNS --export-json $output_path \"$command\""
    return 0
  fi
  hyperfine --warmup "$WARMUP_RUNS" --runs "$MEASURE_RUNS" --export-json "$output_path" "$command" >/dev/null
}

QUALITY_INPUT='{"rules":[],"context":{},"quality":{"coverage_percent":90.0,"lint_issues":0,"lint_errors":0,"lint_warnings":0,"cyclomatic_complexity":1,"cognitive_complexity":1,"function_max_lines":20},"thresholds":{"min_coverage":80.0,"max_lint_errors":0,"max_cyclomatic_complexity":10,"max_cognitive_complexity":10,"max_function_lines":100}}'
SECURITY_INPUT='{"text":"fn main() { println!(\"ok\"); }","fail_on":"warning"}'

echo "Scenario: quality_gate"
run_hyperfine \
  "baseline/shell_quality_gate" \
  "$BASELINE_DIR/quality_gate_baseline.json" \
  "bash \"$THEGENT_ROOT/templates/shared/quality-gate.sh\" \"$THEGENT_ROOT\" >/dev/null 2>&1 || true"

run_hyperfine \
  "current/rust_quality_gate" \
  "$CURRENT_DIR/quality_gate_current.json" \
  "cd \"$THEGENT_ROOT/crates\" && printf '%s' '$QUALITY_INPUT' | cargo run -q -p thegent-hooks --bin quality-gate -- >/dev/null 2>&1"

echo "Scenario: security_pipeline"
if command -v gitleaks >/dev/null 2>&1; then
  run_hyperfine \
    "baseline/gitleaks_scan" \
    "$BASELINE_DIR/security_pipeline_baseline.json" \
    "cd \"$THEGENT_ROOT\" && gitleaks detect --no-banner --no-git --source . --max-target-megabytes 5 --timeout 180 >/dev/null 2>&1 || true"
else
  echo "  - baseline/gitleaks_scan skipped (missing gitleaks)"
fi

run_hyperfine \
  "current/rust_security_pipeline" \
  "$CURRENT_DIR/security_pipeline_current.json" \
  "cd \"$THEGENT_ROOT/crates\" && printf '%s' '$SECURITY_INPUT' | cargo run -q -p thegent-hooks --bin security-pipeline -- >/dev/null 2>&1"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "{}" >"$SUMMARY_PATH"
  echo "# Dry Run" >"$REPORT_PATH"
else
  python3 "$THEGENT_ROOT/scripts/benchmark-report.py" \
    --baseline-dir "$BASELINE_DIR" \
    --current-dir "$CURRENT_DIR" \
    --report-path "$REPORT_PATH" \
    --summary-path "$SUMMARY_PATH" \
    --title "WL-007 Rust Quality/Security Benchmark"
fi

ln -sfn "$RUN_STAMP" "$RESULTS_ROOT/latest"
echo "Benchmark complete: $RUN_DIR"
