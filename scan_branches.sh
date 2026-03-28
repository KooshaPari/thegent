#!/bin/bash
ROOT_DIR="/Users/kooshapari/CodeProjects/Phenotype/repos"
REPOS_FILE="$ROOT_DIR/repos_to_process.txt"
OUTPUT_FILE="$ROOT_DIR/branches_to_open.txt"

rm -f "$OUTPUT_FILE"

while read -r repo; do
    [ -z "$repo" ] && continue
    REPO_PATH="$ROOT_DIR/$repo"
    if [ ! -d "$REPO_PATH" ]; then
        echo "Skipping $repo: not a directory"
        continue
    fi
    cd "$REPO_PATH" || continue
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

    # List local branches, excluding the default branch
    BRANCHES=$(git branch --format='%(refname:short)' | grep -v "^$DEFAULT_BRANCH$")

    for branch in $BRANCHES; do
        # Check if this branch has unique commits by Koosha compared to the default branch
        COMMITS=$(git log "$DEFAULT_BRANCH..$branch" --author="Koosha" --oneline 2>/dev/null)
        if [ -n "$COMMITS" ]; then
            # Check if an open PR already exists for this branch
            # Use REST API (gh api) if rate limited, but gh pr list is standard
            PR_EXISTS=$(gh pr list --head "$branch" --json state --jq '.[0].state' 2>/dev/null)
            if [ "$PR_EXISTS" != "OPEN" ]; then
                # Get the first commit message
                FIRST_MSG=$(git log "$DEFAULT_BRANCH..$branch" --format=%s -1 2>/dev/null)
                echo "$repo|$branch|$DEFAULT_BRANCH|$FIRST_MSG" >> "$OUTPUT_FILE"
            fi
        fi
    done
done < "$REPOS_FILE"
