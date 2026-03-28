#!/usr/bin/env bash
# Script to disable billable CI runs across repos
# Usage: ./scripts/disable-billable-runs.sh <repo_dir>

set -euo pipefail

REPO_DIR="${1:-.}"

echo "=== Disabling billable CI runs in $REPO_DIR ==="

# Find all workflow files with pull_request triggers
find "$REPO_DIR/.github/workflows" -name "*.yml" -o -name "*.yaml" 2>/dev/null | while read wf; do
    if grep -q "pull_request:" "$wf" 2>/dev/null; then
        echo "Processing: $wf"
        
        # Check if already disabled
        if grep -q "NOTE: Billable runs disabled" "$wf" 2>/dev/null; then
            echo "  Already disabled, skipping"
            continue
        fi
        
        # Create backup
        cp "$wf" "$wf.bak"
        
        # Read the file and modify
        {
            echo '# NOTE: Billable runs disabled - use pre-commit/pre-push hooks for validation'
            echo '# Uncomment below to re-enable when GitHub Actions minutes are available'
            echo '# on:'
            echo '#   pull_request:'
            
            # Get lines after "on:" and before first job:
            awk '
            /^on:/ {
                print "# on:"
                in_on_block = 1
                next
            }
            in_on_block && /^  [a-z]/ {
                print "#   "$0
                next
            }
            in_on_block && /^jobs:/ {
                print "on:"
                print "  workflow_dispatch:"
                print "  schedule:"
                print "    - cron: \"0 7 * * *\""
                print ""
                in_on_block = 0
            }
            { print }
            ' "$wf.bak" > "$wf"
        } || {
            echo "  Error processing, restoring backup"
            mv "$wf.bak" "$wf"
            continue
        }
        
        rm -f "$wf.bak"
        echo "  Done"
    fi
done

echo "=== Complete ==="
