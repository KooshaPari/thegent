#!/bin/zsh
# Hook: PostToolUse (Edit|Write)
# Purpose: Merged hook that:
#   1. Accumulates a session-level change manifest (from track-changes.sh)
#   2. Detects "change boundaries" — significant patterns that warrant per-change docs
#
# The Stop hook reads the manifest for reconciliation.
# Change boundary suggestions fire at most once per detected pattern.

set -euo pipefail
HOOK_NAME="CHANGE-DOC-TRACKER"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Initialize variables if not set by hook_init/dispatcher
PROJECT_DIR="${PROJECT_DIR:-.}"
now="${now:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
TOOL_NAME="${TOOL_NAME:-Edit}"
CHANGE_LOG="${CHANGE_LOG:-$HOME/.claude/session-changes.log}"

# Stderr message on unexpected failure (set -e)
trap 'echo "CHANGE-DOC-TRACKER FAIL: unexpected error at line $LINENO" >&2' ERR

# Skip if no file path
[[ -z "$FILE_PATH" ]] && exit 0

# Resolve project root
CLAUDE_DIR="$PROJECT_DIR/.claude"
MARKER_FILE="$CLAUDE_DIR/change-boundary.marker"

# --- Part 1: Change logging (merged from track-changes.sh) ---
# Ensure .claude dir exists (should already, but guard)
[[ -d "$CLAUDE_DIR" ]] || exit 0

# Append: timestamp | tool | file_path
echo "${now}|${TOOL_NAME}|${FILE_PATH}" >> "$CHANGE_LOG"

# --- Part 2: Change boundary detection ---
# Only proceed if docs/changes/ exists (project opted in to change docs)
CHANGES_DIR="$PROJECT_DIR/docs/changes"
[[ -d "$CHANGES_DIR" ]] || exit 0

# Only proceed if the change log has enough entries to analyze
[[ -f "$CHANGE_LOG" ]] || exit 0

# Count lines using bash builtin (no wc spawn)
TOTAL_LINES=0
while IFS= read -r _; do
  (( TOTAL_LINES++ ))
done < "$CHANGE_LOG"
[[ "$TOTAL_LINES" -lt 3 ]] && exit 0

# Ensure marker file exists
[[ -f "$MARKER_FILE" ]] || : >> "$MARKER_FILE"

# Single awk pass: collect stats, config hits, common write dir, and affected areas
# Eliminates 4 separate awk invocations + grep
read -r UNIQUE_DIRS UNIQUE_FILES NEW_FILES CONFIG_HITS COMMON_NEW_DIR AFFECTED_AREAS <<< "$(awk -F'|' '
{
    file = $3
    tool = $2
    if (file == "") next

    # Track unique files
    if (!(file in seen_files)) {
        seen_files[file] = 1
        file_count++

        # Extract directory (everything up to last /)
        dir = file
        gsub(/\/[^\/]*$/, "", dir)
        if (!(dir in seen_dirs)) {
            seen_dirs[dir] = 1
            dir_count++

            # Build affected areas string (last two path components)
            n = split(dir, parts, "/")
            if (n >= 2) short = parts[n-1] "/" parts[n]
            else short = parts[n]
            if (!(short in seen_short)) {
                seen_short[short] = 1
                if (area_count > 0) areas = areas ", "
                areas = areas short
                area_count++
            }
        }
    }

    # Track new files (Write tool, not Edit)
    if (tool == "Write" && !(file in seen_write)) {
        seen_write[file] = 1
        new_file_count++
        wdir = file
        gsub(/\/[^\/]*$/, "", wdir)
        write_dirs[wdir]++
    }

    # Config/schema hits
    if (file ~ /\/(config|schema|migration|\.env|docker-compose|Makefile|Taskfile|go\.mod|go\.sum|package\.json|pyproject\.toml|Cargo\.toml)/) {
        config_count++
    }
}
END {
    # Find common write directory (>=2 writes)
    common_wdir = ""
    for (d in write_dirs) {
        if (write_dirs[d] >= 2) { common_wdir = d; break }
    }
    if (area_count == 0) areas = "various"
    # Use \x1f (unit separator) to delimit common_wdir which may contain spaces
    printf "%d %d %d %d\x1f%s\x1f%s", dir_count, file_count, new_file_count, config_count+0, common_wdir, areas
}
' "$CHANGE_LOG")"

# Parse the unit-separator-delimited fields
IFS=$'\x1f' read -r _nums COMMON_NEW_DIR AFFECTED_AREAS <<< "$UNIQUE_DIRS $UNIQUE_FILES $NEW_FILES $CONFIG_HITS"$'\x1f'"$COMMON_NEW_DIR"$'\x1f'"$AFFECTED_AREAS"
# Re-split numeric fields (they were in UNIQUE_DIRS temporarily)
read -r UNIQUE_DIRS UNIQUE_FILES NEW_FILES CONFIG_HITS <<< "$_nums"

# Detect pattern type — use cached $now date parts (no date spawns)
# Extract date stamp from $now (already set by common.sh): 2026-02-14T12:34:56Z -> 20260214-1234
DATESTAMP="${now:0:4}${now:5:2}${now:8:2}-${now:11:2}${now:14:2}"

PATTERN=""
SUGGESTION_NAME=""

if [[ "$CONFIG_HITS" -ge 2 ]]; then
    PATTERN="architecture-change"
    SUGGESTION_NAME="arch-${DATESTAMP}"
elif [[ "$UNIQUE_DIRS" -ge 3 ]]; then
    PATTERN="cross-cutting"
    SUGGESTION_NAME="cross-${DATESTAMP}"
elif [[ "$NEW_FILES" -ge 2 && -n "$COMMON_NEW_DIR" ]]; then
    PATTERN="new-feature"
    SUGGESTION_NAME="${COMMON_NEW_DIR##*/}-${DATESTAMP}"
fi

# No significant pattern detected
[[ -z "$PATTERN" ]] && exit 0

# Build a fingerprint for this pattern to avoid repeating
FINGERPRINT="${PATTERN}:${UNIQUE_DIRS}d:${UNIQUE_FILES}f"

# Check if we already fired for this fingerprint (bash builtin, no grep spawn)
while IFS= read -r _line; do
  [[ "$_line" == *"$FINGERPRINT"* ]] && exit 0
done < "$MARKER_FILE"

# Record the fingerprint so we don't fire again
echo "$FINGERPRINT" >> "$MARKER_FILE"

# Output the suggestion (printf instead of cat heredoc — equivalent but explicit)
printf 'CHANGE BOUNDARY DETECTED: %s files changed across %s directories\nPattern: %s\nAffected areas: %s\nConsider creating: docs/changes/%s/proposal.md\n' \
  "$UNIQUE_FILES" "$UNIQUE_DIRS" "$PATTERN" "$AFFECTED_AREAS" "$SUGGESTION_NAME"

exit 0
