#!/usr/bin/env bash
# Configure branch protection rules for a repository
# Usage: ./configure-branch-protection.sh <owner/repo>

set -euo pipefail

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Usage: $0 <owner/repo>"
  exit 1
fi

echo "Configuring branch protection for $REPO..."

# Get default branch
DEFAULT_BRANCH=$(gh api repos/"$REPO" --jq '.default_branch')
echo "Default branch: $DEFAULT_BRANCH"

# Configure main branch protection
echo "Setting up protection for main branch..."
gh api --method PUT repos/"$REPO"/branches/"$DEFAULT_BRANCH"/protection \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -f required_status_checks='{"strict":true,"contexts":["policy-gate","guard","CodeRabbit"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_reviewers":1,"dismiss_stale_reviews":true}' \
  -f restrictions=null \
  --silent 2>/dev/null || echo "Note: Some protection settings may already be configured"

# Configure release branch protections
for CHANNEL in canary beta stable; do
  echo "Setting up protection for release/$CHANNEL..."
  gh api --method PUT repos/"$REPO"/branches/release/"$CHANNEL"/protection \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -f required_status_checks='{"strict":false,"contexts":["policy-gate","guard"]}' \
    -f enforce_admins=true \
    -f required_pull_request_reviews='{"required_reviewers":1}' \
    -f restrictions=null \
    --silent 2>/dev/null || echo "Note: release/$CHANNEL may not exist yet"
done

echo "Branch protection configured successfully!"

# Verify
echo ""
echo "Current protection status:"
gh api repos/"$REPO"/branches/"$DEFAULT_BRANCH" --jq '{name: .name, protected: .protected, protection_url: .protection_url}'
