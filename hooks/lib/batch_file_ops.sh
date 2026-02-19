#!/usr/bin/env bash
# Batch File Operations Shell Wrapper
#
# Provides shell-friendly wrappers around the Python batch_file_ops module.
# Reduces shell script verbosity when performing multi-file operations.
#
# Usage:
#   batch_read_files file1 file2 file3
#   batch_write_files path1:content1 path2:content2 ...
#   batch_edit_files path:search:replace path:search:replace ...
#   batch_delete_files file1 file2 file3
#
# Environment:
#   BATCH_FILE_OPS_VERBOSE: Set to 1 for verbose output

set -euo pipefail

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATCH_FILE_OPS_PY="${SCRIPT_DIR}/scripts/batch_file_ops.py"

if [[ ! -f "$BATCH_FILE_OPS_PY" ]]; then
    echo "ERROR: batch_file_ops.py not found at $BATCH_FILE_OPS_PY" >&2
    return 1 2>/dev/null || exit 1
fi

# Batch read files
batch_read_files() {
    local verbose_flag=""
    [[ "${BATCH_FILE_OPS_VERBOSE:-0}" == "1" ]] && verbose_flag="--verbose"

    python3 "$BATCH_FILE_OPS_PY" --read "$@" $verbose_flag
}

# Batch write files
# Expects arguments in format: path:content path:content ...
batch_write_files() {
    local verbose_flag=""
    [[ "${BATCH_FILE_OPS_VERBOSE:-0}" == "1" ]] && verbose_flag="--verbose"

    local -a write_args=()
    for arg in "$@"; do
        # Split path:content on first colon
        local path="${arg%%:*}"
        local content="${arg#*:}"
        write_args+=("$path" "$content")
    done

    python3 "$BATCH_FILE_OPS_PY" --write "${write_args[@]}" $verbose_flag
}

# Batch edit files
# Expects arguments in format: path:search:replace path:search:replace ...
batch_edit_files() {
    local verbose_flag=""
    [[ "${BATCH_FILE_OPS_VERBOSE:-0}" == "1" ]] && verbose_flag="--verbose"

    local -a edit_args=()
    for arg in "$@"; do
        # Split on colons (path:search:replace)
        # This is simplistic; for complex content use Python directly
        local IFS=':'
        read -ra parts <<< "$arg"
        if [[ ${#parts[@]} -lt 3 ]]; then
            echo "ERROR: Edit format must be path:search:replace" >&2
            return 1
        fi
        edit_args+=("${parts[0]}" "${parts[1]}" "${parts[2]}")
    done

    python3 "$BATCH_FILE_OPS_PY" --edit "${edit_args[@]}" $verbose_flag
}

# Batch delete files
batch_delete_files() {
    local verbose_flag=""
    [[ "${BATCH_FILE_OPS_VERBOSE:-0}" == "1" ]] && verbose_flag="--verbose"

    python3 "$BATCH_FILE_OPS_PY" --delete "$@" $verbose_flag
}

# Get backup directory from last operation (if JSON output available)
batch_get_backup_dir() {
    local json_output="$1"
    echo "$json_output" | python3 -c "import sys, json; print(json.load(sys.stdin).get('backup_dir', ''))"
}

export -f batch_read_files batch_write_files batch_edit_files batch_delete_files batch_get_backup_dir
