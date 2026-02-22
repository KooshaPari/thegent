# Autosync Enablement Checklist

This guide provides a step-by-step process to enable and deploy autosync functionality in thegent.

## Prerequisites

Before enabling autosync, ensure you have:

- GitHub account with admin access to target repositories
- Personal access token (PAT) with the following scopes:
  - `repo` (full control of private repositories)
  - `workflow` (update GitHub Actions workflows)
  - `read:org` (read organization data)
- Local development environment with thegent installed
- Access to repository settings and GitHub Actions

## Step-by-Step Enablement Guide

### 1. Environment Variables

Set the required environment variables in your shell profile (`.zshrc`, `.bashrc`, etc.):

```bash
# Enable autosync feature
export THEGENT_AUTOSYNC_ENABLED=1

# Set sync interval (in seconds; recommend 3600 for hourly)
export THEGENT_SYNC_INTERVAL=3600

# GitHub personal access token
export THEGENT_GH_TOKEN="ghp_YOUR_TOKEN_HERE"
```

Verify the environment variables are set:

```bash
echo $THEGENT_AUTOSYNC_ENABLED
echo $THEGENT_SYNC_INTERVAL
echo $THEGENT_GH_TOKEN
```

### 2. Verify Prerequisite Scopes

Your GitHub token must have the required scopes. Check your token at https://github.com/settings/tokens:

- [ ] `repo` scope enabled
- [ ] `workflow` scope enabled
- [ ] `read:org` scope enabled

### 3. Enable GitHub Actions Workflows

Ensure GitHub Actions is enabled in your target repositories:

```bash
# For each repository, visit:
# https://github.com/<owner>/<repo>/settings/actions

# Verify:
# - Actions is enabled
# - Workflows can run
# - Required runner is available
```

### 4. Review Sync Policy

Before enabling autosync, review the sync policy configuration:

```bash
# View current sync policy
thegent config show --filter sync_policy

# Accept the policy (interactive prompt)
thegent config accept-policy sync
```

### 5. Verify Endpoint Reachability

Test connectivity to GitHub and other endpoints:

```bash
# Run startup validation
python -c "
from thegent.integrations.startup_validation import StartupValidator
validator = StartupValidator()
result = validator.validate_all({
    'endpoints': ['https://api.github.com']
})
print(f'Validation passed: {result.passed}')
print(f'Errors: {result.errors}')
print(f'Warnings: {result.warnings}')
"
```

### 6. Test with Non-Production Repository

Create or use a test repository to verify autosync behavior before production deployment:

```bash
# Create a test repository
gh repo create test-autosync --private --source=. --remote=origin --push

# Enable autosync for this repository
export THEGENT_TARGET_REPOS="test-autosync"

# Monitor logs
tail -f ~/.thegent/logs/sync.log
```

## Migration Steps for Existing Repositories

### Step 1: Backup Current State

Before migrating an existing repository to autosync:

```bash
# Export current sync state
thegent export-state --repo <owner>/<repo> --format json > backup_state.json

# Commit backup to repository
git add backup_state.json
git commit -m "chore: backup pre-autosync state"
git push
```

### Step 2: Enable Autosync

```bash
# Configure the repository for autosync
export THEGENT_TARGET_REPOS="<owner>/<repo>"
export THEGENT_AUTOSYNC_ENABLED=1

# Dry-run first to verify behavior
thegent sync --dry-run --repo <owner>/<repo>
```

### Step 3: Monitor Initial Sync

After enabling autosync, monitor the first sync cycle:

```bash
# Watch sync logs in real-time
thegent logs follow --filter autosync

# Check sync status
thegent sync status --repo <owner>/<repo>
```

### Step 4: Verify Data Integrity

After the first sync completes, verify that data integrity is maintained:

```bash
# Compare pre- and post-sync states
thegent verify-integrity --repo <owner>/<repo> --baseline backup_state.json
```

## Rollback Procedure

If issues occur after enabling autosync, follow this rollback procedure:

### Immediate Rollback (< 5 minutes)

```bash
# Disable autosync immediately
export THEGENT_AUTOSYNC_ENABLED=0

# Verify it's disabled
thegent config show --filter autosync_enabled

# Stop any running sync processes
thegent stop-sync --force
```

### Data Restoration (if needed)

```bash
# Restore from backup
thegent restore-state --repo <owner>/<repo> --from backup_state.json

# Verify restoration
thegent verify-integrity --repo <owner>/<repo>

# Push restored state
git push --force-with-lease
```

### Post-Rollback Investigation

```bash
# Collect logs for analysis
thegent logs export --filter autosync --since 1h > rollback_analysis.log

# Review sync policy for issues
thegent config show --filter sync_policy > policy_snapshot.json

# File issue with logs and policy
gh issue create --title "Autosync rollback analysis" --body "See attached logs"
```

## Verification Commands

Use these commands to verify autosync is working correctly:

```bash
# 1. Check autosync is enabled
test -n "$THEGENT_AUTOSYNC_ENABLED" && echo "Enabled" || echo "Disabled"

# 2. Verify sync configuration
thegent config show --filter "sync|autosync"

# 3. Check latest sync status
thegent sync status --repo <owner>/<repo>

# 4. View sync history
thegent logs list --filter autosync --last 10

# 5. Run startup validation
python -m thegent.integrations.startup_validation --config config.json

# 6. Check reflection event log
ls -la docs/reference/reflection_events.jsonl
wc -l docs/reference/reflection_events.jsonl

# 7. Monitor active sync processes
thegent ps --filter autosync
```

## Troubleshooting

### Autosync Not Running

**Issue**: Autosync is enabled but sync cycles are not executing.

**Solution**:

```bash
# Check if autosync is truly enabled
env | grep THEGENT_AUTOSYNC

# Verify sync interval is set
env | grep THEGENT_SYNC_INTERVAL

# Check for errors in logs
thegent logs follow --filter error --since 10m

# Restart thegent service
thegent restart
```

### Authentication Failures

**Issue**: Sync fails with authentication errors.

**Solution**:

```bash
# Verify token is present and valid
gh auth status

# Test token scopes
gh api user

# Regenerate token if necessary
# Visit: https://github.com/settings/tokens

# Update environment
export THEGENT_GH_TOKEN="ghp_NEW_TOKEN_HERE"
```

### Sync Policy Violations

**Issue**: Sync is blocked due to policy violations.

**Solution**:

```bash
# Review current policy
thegent config show --filter sync_policy

# Check strict mapping mode
python -c "
from thegent.integrations.strict_mapping import StrictMappingValidator
validator = StrictMappingValidator()
print('Strict mapping enabled')
"

# Review reflection event log for conflicts
tail -n 20 docs/reference/reflection_events.jsonl | jq 'select(.decision_type == "conflict")'
```

## Post-Enablement Monitoring

After successfully enabling autosync:

1. Monitor sync logs daily for the first week
2. Review reflection event log for decision patterns
3. Track sync performance metrics
4. Gather feedback from team members
5. Schedule monthly review of sync policy

For questions or issues, refer to the main documentation at `docs/guides/` or contact the thegent team.
