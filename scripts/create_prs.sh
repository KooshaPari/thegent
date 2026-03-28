#!/bin/bash
# Create PRs sequentially with delays

REPOS="4sgm civ cliproxyapi-plusplus tokenledger trace phenodocs helios-cli"

for repo in $REPOS; do
  echo "Creating PR for $repo..."
  cd /Users/kooshapari/CodeProjects/Phenotype/repos
  gh pr create -R "KooshaPari/$repo" \
    --title "sync: merge upstream main" \
    --body "Sync fork with upstream" \
    --base main \
    --head phenotype/upstream-sync-20260324 2>&1
  echo "Waiting 60 seconds..."
  sleep 60
done
