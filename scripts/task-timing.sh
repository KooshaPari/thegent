#!/usr/bin/env zsh
# Task timing script
# Measures and displays how long tasks take to execute

set -e

TASK="${1:-}"

if [ -z "$TASK" ]; then
    echo "Usage: task-timing <task-name>"
    echo "Measures execution time for a task"
    exit 1
fi

START_TIME=$(date +%s.%N)
task "$TASK"
END_TIME=$(date +%s.%N)

ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)

echo ""
echo "[bold green]Task '$TASK' completed in ${ELAPSED}s[/bold green]"

# Store timing data
TIMING_DIR="${TIMING_DIR:-.task-timings}"
mkdir -p "$TIMING_DIR"
echo "$(date +%Y-%m-%dT%H:%M:%S),$TASK,$ELAPSED" >> "$TIMING_DIR/timings.csv"
