#!/usr/bin/env zsh
# Reproducible benchmark harness for shell-vs-rust hook runtime comparisons.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_ROOT="${THEGENT_BENCH_RESULTS_DIR:-$THEGENT_ROOT/benchmarks/results}"
WARMUP_RUNS="${BENCH_WARMUP_RUNS:-3}"
MEASURE_RUNS="${BENCH_MEASURE_RUNS:-20}"
DRY_RUN="${BENCH_DRY_RUN:-0}"

export LC_ALL=C
export TZ=UTC

if ! command -v hyperfine >/dev/null 2>&1; then
  echo "benchmark-comprehensive: missing required dependency: hyperfine" >&2
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
MANIFEST_PATH="$RUN_DIR/manifest.json"

mkdir -p "$BASELINE_DIR" "$CURRENT_DIR"

echo "Benchmark run: $RUN_STAMP"
echo "Results dir:   $RUN_DIR"
echo "Warmup runs:   $WARMUP_RUNS"
echo "Measure runs:  $MEASURE_RUNS"
echo ""

run_hyperfine() {
  local label="$1"
  local output_path="$2"
  local command="$3"
  echo "  - $label"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "    [dry-run] hyperfine --warmup $WARMUP_RUNS --runs $MEASURE_RUNS --export-json $output_path $command"
    return 0
  fi
  hyperfine \
    --warmup "$WARMUP_RUNS" \
    --runs "$MEASURE_RUNS" \
    --export-json "$output_path" \
    "$command" \
    >/dev/null
}

echo "Scenario: tool_detection"
run_hyperfine \
  "baseline/bash" \
  "$BASELINE_DIR/tool_detection_bash.json" \
  "bash -lc 'source \"$THEGENT_ROOT/hooks/lib/common.sh\"; JQ_CMD=\"\$(command -v jq 2>/dev/null || echo jq)\"; RG_CMD=\"\$(command -v rg 2>/dev/null || true)\"; FD_CMD=\"\$(command -v fd 2>/dev/null || true)\"; echo \"\$JQ_CMD\$RG_CMD\$FD_CMD\" >/dev/null'"

if command -v thegent-tool-detect >/dev/null 2>&1; then
  run_hyperfine \
    "current/rust" \
    "$CURRENT_DIR/tool_detection_rust.json" \
    "thegent-tool-detect --json"
else
  echo "  - current/rust skipped (missing thegent-tool-detect)"
fi

echo "Scenario: path_resolution"
run_hyperfine \
  "baseline/bash" \
  "$BASELINE_DIR/path_resolution_bash.json" \
  "bash -lc 'for dir in \${PATH//:/ }; do if [[ -x \"\$dir/codex\" ]]; then echo \"\$dir/codex\"; break; fi; done'"

if command -v thegent-path-resolve >/dev/null 2>&1; then
  run_hyperfine \
    "current/rust" \
    "$CURRENT_DIR/path_resolution_rust.json" \
    "thegent-path-resolve codex"
else
  echo "  - current/rust skipped (missing thegent-path-resolve)"
fi

echo "Scenario: process_scanning"
run_hyperfine \
  "baseline/python" \
  "$BASELINE_DIR/process_scanning_python.json" \
  "python3 -c 'import subprocess; subprocess.run([\"ps\", \"aux\"], capture_output=True, check=True)'"

if python3 -c "from thegent_discovery import DiscoveryInterface" >/dev/null 2>&1; then
  run_hyperfine \
    "current/rust" \
    "$CURRENT_DIR/process_scanning_rust.json" \
    "python3 -c 'from thegent_discovery import DiscoveryInterface; DiscoveryInterface().scan_agents()'"
else
  echo "  - current/rust skipped (missing import: thegent_discovery)"
fi

if [[ "$DRY_RUN" == "1" ]]; then
  echo "{}" >"$SUMMARY_PATH"
  echo "# Dry Run\n" >"$REPORT_PATH"
fi

cat >"$MANIFEST_PATH" <<EOF
{
  "run_id": "$RUN_STAMP",
  "generated_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_sha": "$RUN_SHA",
  "warmup_runs": $WARMUP_RUNS,
  "measure_runs": $MEASURE_RUNS,
  "dry_run": $DRY_RUN,
  "baseline_dir": "$BASELINE_DIR",
  "current_dir": "$CURRENT_DIR"
}
EOF

if [[ "$DRY_RUN" != "1" ]]; then
  python3 "$THEGENT_ROOT/scripts/benchmark-report.py" \
    --baseline-dir "$BASELINE_DIR" \
    --current-dir "$CURRENT_DIR" \
    --report-path "$REPORT_PATH" \
    --summary-path "$SUMMARY_PATH" \
    --title "Rust Hook Benchmark Comparison"
fi

ln -sfn "$RUN_STAMP" "$RESULTS_ROOT/latest"

echo ""
echo "Benchmarking complete"
echo "Run directory: $RUN_DIR"
echo "Manifest:      $MANIFEST_PATH"
echo "Report:        $REPORT_PATH"
echo "Summary JSON:  $SUMMARY_PATH"
