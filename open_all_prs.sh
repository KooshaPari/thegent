#!/bin/bash
REPO=$1
grep "^$REPO|" branches_to_open.txt | while read -r line; do
    BRANCH=$(echo "$line" | cut -d'|' -f2)
    BASE=$(echo "$line" | cut -d'|' -f3)
    MSG=$(echo "$line" | cut -d'|' -f4)
    
    echo "Processing $REPO:$BRANCH..."
    
    cd "/Users/kooshapari/CodeProjects/Phenotype/repos/$REPO" || continue
    
    # Check if branch is in a worktree
    WORKTREE=$(git worktree list --porcelain | grep -B 2 "branch refs/heads/$BRANCH" | head -n 1 | cut -d' ' -f2)
    
    if [ -n "$WORKTREE" ]; then
        echo "Using worktree $WORKTREE for $BRANCH"
        TARGET_DIR="$WORKTREE"
    else
        echo "Using repo dir for $BRANCH"
        git checkout "$BRANCH" || continue
        TARGET_DIR="/Users/kooshapari/CodeProjects/Phenotype/repos/$REPO"
    fi
    
    cd "$TARGET_DIR" || continue
    git push origin HEAD
    gh pr create --base "$BASE" --title "$MSG" --body "## Summary\n$MSG\n\ncc @kooshapari" --repo "KooshaPari/$REPO" || echo "Failed to create PR for $BRANCH"
    
    cd "/Users/kooshapari/CodeProjects/Phenotype/repos"
done
