#!/usr/bin/env bash
# git-changed.sh — Git-aware change detection utilities for hooks
# Provides functions to get changed files, filter by pattern, and check specific files
# Usage: source this file to use the functions

# Guard against double-sourcing
[[ -n "${_HOOK_GIT_CHANGED_LOADED:-}" ]] && return 0
_HOOK_GIT_CHANGED_LOADED=1

# Get list of files changed since last commit (staged + unstaged)
# Usage: git_changed_files
git_changed_files() {
    git diff --name-only HEAD 2>/dev/null || true
}

# Get files changed between two refs
# Usage: git_changed_files_between "main" "feature-branch"
git_changed_files_between() {
    local from="$1" to="$2"
    git diff --name-only "$from" "$to" 2>/dev/null || true
}

# Get files changed in the last N commits
# Usage: git_changed_files_in_last_commits 3
git_changed_files_in_last_commits() {
    local count="${1:-1}"
    git diff --name-only HEAD~"$count" HEAD 2>/dev/null || true
}

# Check if specific file changed since last commit
# Usage: git_file_changed "src/main.py" && echo "changed"
git_file_changed() {
    local file="$1"
    git diff --name-only HEAD 2>/dev/null | grep -q "^${file}$"
}

# Get file hash for cache key (content hash, not working tree)
# Usage: git_file_hash "src/main.py"
git_file_hash() {
    local file="$1"
    git hash-object "$file" 2>/dev/null
}

# Get list of untracked (new) files
# Usage: git_untracked_files
git_untracked_files() {
    git ls-files --others --exclude-standard 2>/dev/null || true
}

# Get all changed files (modified + untracked) - combined view
# Usage: git_all_changed_files
git_all_changed_files() {
    {
        git diff --name-only HEAD 2>/dev/null
        git ls-files --others --exclude-standard 2>/dev/null
    } | sort -u
}

# Filter changed files by pattern (regex)
# Usage: git_changed_files | grep_pattern "\.py$"
grep_pattern() {
    local pattern="$1"
    grep -E "$pattern" 2>/dev/null || true
}

# Check if any files match pattern
# Usage: any_changed_match "\.(py|js)$"
any_changed_match() {
    local pattern="$1"
    local changed_files
    changed_files="$(git_changed_files)"
    echo "$changed_files" | grep -qE "$pattern"
}

# Get file extension from path (no subprocess)
# Usage: ext=$(file_ext "src/main.py") -> ext="py"
file_ext() {
    echo "${1##*.}"
}

# Check if changed files include any from specific directories
# Usage: git_any_in_dirs "src/components" "src/utils"
git_any_in_dirs() {
    local changed_files
    changed_files="$(git_changed_files)"
    for dir in "$@"; do
        if echo "$changed_files" | grep -q "^${dir}/"; then
            return 0
        fi
    done
    return 1
}

# Get the current HEAD SHA
# Usage: HEAD_SHA=$(git_current_head)
# Cached version: Returns readonly _GIT_HEAD_SHA if available
git_current_head() {
    # Use cached value if available (set by hook initialization)
    if [[ -n "${_GIT_HEAD_SHA:-}" ]]; then
      echo "$_GIT_HEAD_SHA"
    else
      git rev-parse HEAD 2>/dev/null
    fi
}

# Check if in a git repository
# Usage: in_git_repo && echo "yes"
# Cached version: Returns readonly _GIT_IS_REPO if available (caches result)
in_git_repo() {
    # Use cached result if available
    if [[ -n "${_GIT_IS_REPO_CACHED:-}" ]]; then
      [[ "$_GIT_IS_REPO_CACHED" == "true" ]]
      return
    fi
    # Otherwise check and cache for future use
    if git rev-parse --is-inside-work-tree 2>/dev/null > /dev/null; then
      readonly _GIT_IS_REPO_CACHED="true"
      return 0
    else
      readonly _GIT_IS_REPO_CACHED="false"
      return 1
    fi
}
