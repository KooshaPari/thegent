#!/usr/bin/env zsh
# Enhanced task help script
# Provides detailed help for tasks with examples and dependencies

set -e

TASKFILE="${TASKFILE:-Taskfile.yml}"
TASK="${1:-}"

if [ -z "$TASK" ]; then
    echo "Usage: task-help <task-name>"
    echo ""
    echo "Available tasks:"
    task --list-all 2>/dev/null | grep -E "^\*" | sed 's/^\* //' | head -20
    exit 0
fi

# Get task description
DESC=$(task --list-all 2>/dev/null | grep -E "^\* $TASK" | sed 's/^\* [^:]*: //' || echo "No description")

echo "[bold cyan]${TASK}[/bold cyan]"
echo "$DESC"
echo ""

# Try to extract task details from Taskfile.yml
if [ -f "$TASKFILE" ]; then
    # Extract task definition (basic parsing)
    echo "[bold]Task Definition:[/bold]"
    awk "/^  $TASK:/,/^  [a-z]/ {if (/^  [a-z]/ && !/^  $TASK:/) exit; print}" "$TASKFILE" | head -20
fi

# Show task dependencies if any
echo ""
echo "[bold]Dependencies:[/bold]"
task --list-all 2>/dev/null | grep -E "^\* $TASK" | grep -oE "deps:\[.*\]" || echo "None"

# Show examples if available
if [ -f "docs/tasks/$TASK.md" ]; then
    echo ""
    echo "[bold]Examples:[/bold]"
    cat "docs/tasks/$TASK.md"
fi
