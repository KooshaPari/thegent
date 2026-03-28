#!/bin/bash
ROOT_DIR="/Users/kooshapari/CodeProjects/Phenotype/repos"
REPOS_FILE="${REPOS_FILE:-$ROOT_DIR/repos_to_process.txt}"
OUTPUT_FILE="$ROOT_DIR/branches_to_open.txt"

# Keep existing work if we are restarting, but the user wants a fresh scan
# Actually, I'll just rewrite it to be faster and restart it.
rm -f "$OUTPUT_FILE"

while read -r repo; do
    [ -z "$repo" ] && continue
    REPO_PATH="$ROOT_DIR/$repo"
    if [ ! -d "$REPO_PATH" ]; then
        echo "Skipping $repo: not a directory"
        continue
    fi
    cd "$REPO_PATH" || continue
    echo "Scanning repo in $PWD"
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "Skipping $repo: not a git repository"
        continue
    fi

    # Determine default branch
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|^refs/remotes/origin/||')
    if [ -z "$DEFAULT_BRANCH" ]; then
        DEFAULT_BRANCH=$(git branch --list main master | sed 's/* //;s/ //g' | head -1)
    fi
    [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH="main"

    # Get all open PR head branch names once
    OPEN_PR_BRANCHES=$(gh pr list --state open --limit 500 --json headRefName --jq '.[].headRefName' 2>/dev/null)

    # List local branches, excluding the default branch
    BRANCHES=$(git branch --format='%(refname:short)' | grep -v "^$DEFAULT_BRANCH$")

    for branch in $BRANCHES; do
        # Check if this branch has unique commits by Koosha compared to the default branch
        COMMITS=$(git log "$DEFAULT_BRANCH..$branch" --author="Koosha" --oneline 2>/dev/null)
        if [ -n "$COMMITS" ]; then
            # Check if branch is in the list of open PR branches
            if ! echo "$OPEN_PR_BRANCHES" | grep -qxF "$branch"; then
                # Get the first commit message
                FIRST_MSG=$(git log "$DEFAULT_BRANCH..$branch" --format=%s -1 2>/dev/null)
                echo "$repo|$branch|$DEFAULT_BRANCH|$FIRST_MSG" >> "$OUTPUT_FILE"
            fi
        fi
    done
done < "$REPOS_FILE"
