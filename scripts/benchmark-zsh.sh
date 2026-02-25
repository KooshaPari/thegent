#!/usr/bin/env bash
# Benchmark ZSH startup time for thegent shell configuration
# Uses hyperfine if available, otherwise falls back to time-based measurement

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="${ROOT_DIR}/benchmarks/results/zsh"
SHELL_DIR="${ROOT_DIR}/shell"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "=== ZSH Shell Benchmark ==="
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Results dir: $RESULTS_DIR"
echo ""

# Check for zsh
if ! command -v zsh &>/dev/null; then
    echo "ERROR: zsh not found"
    exit 1
fi

ZSH_VERSION=$(zsh --version | head -1)
echo "ZSH Version: $ZSH_VERSION"
echo ""

# Function to run benchmark using Python timing
run_fallback_benchmark() {
    local name="$1"
    local cmd="$2"
    local output_file="$3"
    local runs=10

    echo "Running $name ($runs iterations)..."

    # Use Python to run the benchmark
    python3 << EOF
import subprocess
import time
import json
import statistics

cmd = "$cmd"
runs = $runs
output_file = "$output_file"

times = []
for i in range(runs):
    start = time.perf_counter()
    subprocess.run(cmd, shell=True, capture_output=True)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000
    times.append(elapsed_ms)

mean_ms = statistics.mean(times)
stddev_ms = statistics.stdev(times) if len(times) > 1 else 0
min_ms = min(times)
max_ms = max(times)
median_ms = statistics.median(times)

results = {
    "results": [{
        "command": cmd,
        "mean": mean_ms / 1000,
        "stddev": stddev_ms / 1000,
        "min": min_ms / 1000,
        "max": max_ms / 1000,
        "median": median_ms / 1000,
    }]
}

with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"  mean: {mean_ms:.2f}ms")
print(f"  median: {median_ms:.2f}ms")
print(f"  min: {min_ms:.2f}ms")
print(f"  max: {max_ms:.2f}ms")
EOF
}

# Check for hyperfine
HAS_HYPERFINE=0
if command -v hyperfine &>/dev/null; then
    HAS_HYPERFINE=1
    echo "Using hyperfine for benchmarking"
else
    echo "hyperfine not found, using fallback timing"
fi
echo ""

# Run benchmarks
echo "--- Running benchmarks ---"

# 1. Baseline zsh (no config)
echo "1. Baseline zsh (no config)..."
if [[ $HAS_HYPERFINE -eq 1 ]]; then
    hyperfine \
        --warmup 3 \
        --runs 10 \
        --export-json "${RESULTS_DIR}/baseline.json" \
        'zsh -i -c exit' \
        2>/dev/null || run_fallback_benchmark "baseline" "zsh -i -c exit" "${RESULTS_DIR}/baseline.json"
else
    run_fallback_benchmark "baseline" "zsh -i -c exit" "${RESULTS_DIR}/baseline.json"
fi

# 2. thegent zsh config
echo ""
echo "2. thegent zsh config..."
if [[ $HAS_HYPERFINE -eq 1 ]]; then
    hyperfine \
        --warmup 3 \
        --runs 10 \
        --export-json "${RESULTS_DIR}/thegent.json" \
        "ZDOTDIR=${SHELL_DIR} zsh -i -c exit" \
        2>/dev/null || run_fallback_benchmark "thegent" "ZDOTDIR=${SHELL_DIR} zsh -i -c exit" "${RESULTS_DIR}/thegent.json"
else
    run_fallback_benchmark "thegent" "ZDOTDIR=${SHELL_DIR} zsh -i -c exit" "${RESULTS_DIR}/thegent.json"
fi

# 3. Compare with regression check
echo ""
echo "--- Results Summary ---"

# Extract mean times using Python
python3 << EOF
import json
import sys
from pathlib import Path

results_dir = Path("${RESULTS_DIR}")

try:
    baseline_file = results_dir / "baseline.json"
    thegent_file = results_dir / "thegent.json"

    if not baseline_file.exists() or not thegent_file.exists():
        print("⚠️ Benchmark files not found")
        sys.exit(0)

    with open(baseline_file) as f:
        baseline = json.load(f)
    with open(thegent_file) as f:
        thegent = json.load(f)

    baseline_mean = baseline["results"][0]["mean"]
    thegent_mean = thegent["results"][0]["mean"]

    print(f"Baseline zsh:  {baseline_mean:.4f}s ({baseline_mean*1000:.0f}ms)")
    print(f"thegent zsh:   {thegent_mean:.4f}s ({thegent_mean*1000:.0f}ms)")

    if baseline_mean > 0:
        ratio = thegent_mean / baseline_mean
        print(f"Ratio:         {ratio:.2f}x")

        # Check regression
        # Note: Absolute target depends on environment (CI vs local, disk speed, etc.)
        # Focus on relative regression (thegent vs baseline)
        if ratio > 3.0:
            print(f"\n❌ FAIL: thegent is {ratio:.2f}x slower than baseline (>3x)")
            sys.exit(1)
        elif ratio > 2.0:
            print(f"\n⚠️  WARNING: thegent is {ratio:.2f}x slower than baseline")
            # Warning but don't fail
        else:
            print(f"\n✅ OK: thegent overhead is acceptable ({ratio:.2f}x)")

        # Check absolute time (only if baseline is reasonable, i.e., <500ms)
        if baseline_mean < 0.5 and thegent_mean > 0.150:
            print(f"   Note: Absolute time ({thegent_mean*1000:.0f}ms) exceeds 150ms target")
            print(f"   (Baseline was {baseline_mean*1000:.0f}ms)")

except Exception as e:
    print(f"⚠️ Error parsing results: {e}")
    sys.exit(0)
EOF

echo ""
echo "=== Benchmark Complete ==="
echo "Results saved to: ${RESULTS_DIR}"
