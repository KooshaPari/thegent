#!/usr/bin/env zsh
# Run reproducible pytest benchmark slices with explicit run IDs and artifact history.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SCOPE="${BENCH_SCOPE:-routing}"
RESULTS_ROOT="${THEGENT_BENCH_RESULTS_DIR:-$THEGENT_ROOT/benchmarks/results/pybench}"
RUN_SHA="${BENCH_RUN_SHA:-$(git -C "$THEGENT_ROOT" rev-parse --short HEAD 2>/dev/null || echo no-git)}"
RUN_STAMP="${BENCH_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$RUN_SHA}"
RUN_DIR="$RESULTS_ROOT/$RUN_STAMP"
CURRENT_DIR="$RUN_DIR/current"
BASELINE_DIR="$RUN_DIR/baseline"
REPORT_PATH="$RUN_DIR/report.md"
SUMMARY_PATH="$RUN_DIR/summary.json"
MANIFEST_PATH="$RUN_DIR/manifest.json"
HISTORY_PATH="$RESULTS_ROOT/pybench-${SCOPE}-history.json"
TEST_PATH="${BENCH_TEST_PATH:-tests/routing}"
WITH_XDIST="${BENCH_WITH_XDIST:-0}"
WARMUP_RUNS="${BENCH_WARMUP_RUNS:-3}"
MEASURE_RUNS="${BENCH_MEASURE_RUNS:-20}"
DRY_RUN="${BENCH_DRY_RUN:-0}"

if [[ "$WITH_XDIST" == "1" || "$WITH_XDIST" == "true" ]]; then
  XDIST_LABEL="xdist"
  PARALLEL_FLAG=("-n" "auto")
else
  XDIST_LABEL="no-xdist"
  PARALLEL_FLAG=()
fi

SCENARIO="$SCOPE-$XDIST_LABEL"
RESULT_PATH="$CURRENT_DIR/${SCENARIO}.json"

export LC_ALL=C
export TZ=UTC

mkdir -p "$CURRENT_DIR" "$BASELINE_DIR"

echo "Benchmark scope:   $SCENARIO"
echo "Results dir:      $RUN_DIR"
echo "Run ID:          $RUN_STAMP"
echo "Test path:       $TEST_PATH"
echo "xdist:           $WITH_XDIST"
echo "Warmup runs:     $WARMUP_RUNS"
echo "Measure runs:    $MEASURE_RUNS"

echo "Preparing command..."
PYTEST_ARGS=("uv" "run" "pytest" "-q" "--maxfail=1")
if (( ${#PARALLEL_FLAG[@]} > 0 )); then
  PYTEST_ARGS+=("${PARALLEL_FLAG[@]}")
fi
PYTEST_ARGS+=("$TEST_PATH")

run_hyperfine() {

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] hyperfine --warmup $WARMUP_RUNS --runs $MEASURE_RUNS --export-json $RESULT_PATH ${PYTEST_ARGS[*]}"
    return 0
  fi

  hyperfine \
    --warmup "$WARMUP_RUNS" \
    --runs "$MEASURE_RUNS" \
    --export-json "$RESULT_PATH" \
    "${PYTEST_ARGS[@]}" \
    >/dev/null
}

run_hyperfine "$RESULT_PATH"

if [[ "$DRY_RUN" == "0" ]]; then
  python3 - "$RESULT_PATH" "$SUMMARY_PATH" <<'PY'
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

result_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])

payload = json.loads(result_path.read_text(encoding="utf-8"))
results = payload.get("results", [])
if not results:
    raise RuntimeError(f"No hyperfine results for {result_path}")

first = results[0]
summary = {
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "mean_seconds": float(first["mean"]),
    "min_seconds": float(first["min"]),
    "max_seconds": float(first["max"]),
    "stddev_seconds": float(first.get("stddev", 0.0)),
}
summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
fi

python3 - "$RUN_DIR" "$RESULT_PATH" "$RUN_STAMP" "$RUN_SHA" "$SCOPE" "$TEST_PATH" "$WITH_XDIST" "$WARMUP_RUNS" "$MEASURE_RUNS" "$SUMMARY_PATH" "$MANIFEST_PATH" "$HISTORY_PATH" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
result_path = Path(sys.argv[2])
run_id = sys.argv[3]
run_sha = sys.argv[4]
scope = sys.argv[5]
test_path = sys.argv[6]
with_xdist = sys.argv[7] == "1"
warmup_runs = int(sys.argv[8]) if sys.argv[8].isdigit() else 0
measure_runs = int(sys.argv[9]) if sys.argv[9].isdigit() else 0
summary_path = Path(sys.argv[10])
manifest_path = Path(sys.argv[11])
history_path = Path(sys.argv[12])

with result_path.open("r", encoding="utf-8") as fp:
    payload = json.load(fp)

if payload:
    command = [entry.get("command", "") for entry in payload.get("results", []) if entry.get("command")][:1]
else:
    command = []

summary_payload = {}
summary_file = run_dir / "summary.json"
if summary_file.exists():
    summary_payload = json.loads(summary_file.read_text(encoding="utf-8"))

generated_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
results_count = len(payload.get("results", []))
primary_result = payload.get("results", [])[0] if results_count else {}
mean_seconds = primary_result.get("mean")
stddev_seconds = primary_result.get("stddev")

manifest = {
    "run_id": run_id,
    "scope": scope,
    "test_path": test_path,
    "with_xdist": with_xdist,
    "generated_at_utc": generated_at_utc,
    "command": command[0] if command else " ".join(payload.get("command", [])),
    "results_path": str(result_path),
    "git_sha": run_sha,
    "warmup_runs": warmup_runs,
    "measure_runs": measure_runs,
    "result_count": results_count,
    "mean_seconds": float(mean_seconds) if isinstance(mean_seconds, (int, float)) else None,
    "stddev_seconds": float(stddev_seconds) if isinstance(stddev_seconds, (int, float)) else None,
    "hyperfine_export": str(result_path),
    "summary": summary_payload,
    "source_benchmark_output": payload,
}

manifest_text = json.dumps(manifest, indent=2, sort_keys=True)
run_dir.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(manifest_text + "\n", encoding="utf-8")

report = [
    f"# Pytest Benchmark: {scope}",
    "",
    f"- Run ID: {run_id}",
    f"- Scope: `{scope}`",
    f"- Test path: `{test_path}`",
    f"- xdist: `{with_xdist}`",
    f"- Hyperfine result: `{result_path}`",
    "",
]
if summary_payload:
    report.append(f"- Mean runtime (ms): `{summary_payload.get('mean_seconds', 0) * 1000:.3f}`")
    report.append(f"- Stddev (ms): `{summary_payload.get('stddev_seconds', 0) * 1000:.3f}`")

(run_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

history = {
    "schema_version": "benchmark-suite-history/v1",
    "scope": scope,
    "run_ids": [],
}
if history_path.exists():
    history = json.loads(history_path.read_text(encoding="utf-8"))

history.setdefault("schema_version", "benchmark-suite-history/v1")
history.setdefault("scope", scope)
history.setdefault("run_ids", [])

run_items = {item["run_id"]: item for item in history.get("run_ids", [])}
run_items[run_id] = manifest

ordered_runs = sorted(
    run_items.values(),
    key=lambda item: item.get("generated_at_utc", ""),
    reverse=True,
)

history["run_ids"] = ordered_runs[:50]
history_path.parent.mkdir(parents=True, exist_ok=True)
history_path.write_text(
    json.dumps(history, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

ln -sfn "$RUN_STAMP" "$RESULTS_ROOT/latest-$SCENARIO"

echo "Benchmark complete."
echo "Run directory: $RUN_DIR"
echo "Manifest:      $MANIFEST_PATH"
echo "Report:        $REPORT_PATH"
echo "Summary:       $SUMMARY_PATH"
