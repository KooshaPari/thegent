# Documentation Release Process

## Overview

This document outlines the complete process for releasing a new version of the Ante documentation. The process is divided into three phases: Pre-Release, Release, and Post-Release.

**Average Duration:** 2-3 hours per release  
**Release Frequency:** Every 2-4 weeks for minor releases, quarterly+ for major releases

## Pre-Release Phase (1-2 days before release)

### 1. Prepare Release Notes
**Owner:** Documentation Lead

- [ ] Gather all changes since last release
- [ ] Review git history or change log
- [ ] Categorize changes:
  - New content (document in RELEASES.md)
  - Updated content (note in RELEASES.md)
  - Deprecated content (add deprecation notices)
  - Removed content (document in migration guide)
  - Bug fixes (note in changelog)

**Deliverable:** Draft release notes with all changes categorized

### 2. Create Release Branch
**Owner:** Documentation Lead

```bash
# Create release branch from main
git checkout -b release/docs-v1.X.X

# Or if using Git Flow
git flow release start 1.X.X
```

**Naming Convention:** `release/docs-vX.Y.Z` (following semantic versioning)

### 3. Update Version References
**Owner:** Documentation Lead

Update version numbers in:
- [ ] `docs/context/releases/RELEASES.md` - Add new release entry at top
- [ ] `package.json` or version file (if applicable) - Update docs version
- [ ] Website config (if applicable) - Update current version
- [ ] `docs/context/releases/VERSION_COMPATIBILITY.md` - Update compatibility matrix
- [ ] Any release status indicators

**Example changes to RELEASES.md:**
```markdown
### 1.X.Z
**Released:** [Today's Date]  
**Compatible with:** Ante X.Y.Z - X.Y.x  
**Current Status:** Active - Latest Release

#### Summary of Changes
[Your summary here]
```

### 4. Content Validation
**Owner:** Documentation Team

- [ ] Check all links are valid (internal and external)
- [ ] Verify all code examples execute correctly
- [ ] Review grammar and spelling across new/updated content
- [ ] Validate markdown formatting
- [ ] Check that images render correctly
- [ ] Verify tables and lists format properly
- [ ] Test navigation and search functionality

**Tools:**
- Link checker: `npm run check-links` (if available)
- Spell check: `npm run spell-check` (if available)
- Manual review: Read through all updated sections

### 5. Ante Version Compatibility Check
**Owner:** DevOps / Technical Lead

- [ ] Verify compatibility with target Ante versions
- [ ] Test code examples against compatible Ante versions
- [ ] Check for deprecated Ante features in documentation
- [ ] Update any feature references that changed in Ante

**Checklist:**
- [ ] All CLI examples work with target Ante versions
- [ ] API examples match current Ante API
- [ ] Configuration examples are valid for target versions
- [ ] No references to deprecated Ante features

### 6. Create Pull Request for Release
**Owner:** Documentation Lead

```bash
git push origin release/docs-vX.Y.Z
```

**PR Title:** `docs: Release documentation v1.X.Z`

**PR Description Template:**
```markdown
## Release: Documentation v1.X.Z

**Release Date:** [Date]  
**Ante Compatibility:** [version range]  
**Release Type:** [Major / Minor / Patch / Hotfix]

### Changes Summary
[Brief summary of changes]

### New Content
- [List new sections]

### Updated Content  
- [List updated sections]

### Breaking Changes
- [List any breaking changes, or "None"]

### Validation Checklist
- [ ] All links verified
- [ ] Code examples tested
- [ ] Grammar and spelling checked
- [ ] Ante compatibility verified
- [ ] Version references updated
- [ ] Release notes complete

### Related Issues
Closes #[issue number] if applicable
```

### 7. Review and Approval
**Owner:** Documentation Team Lead

- [ ] Review all changes in PR
- [ ] Verify release notes are complete
- [ ] Check version numbering is correct
- [ ] Approve PR for merge

**Required reviewers:** 1+ (usually doc team lead)  
**Required checks:** All automated checks pass

---

## Release Phase (Release day)

### 1. Merge Release Branch
**Owner:** Documentation Lead

```bash
# Merge PR after approval
# Use "Squash and merge" or "Create a merge commit" based on your workflow
```

**Verify:** Main branch now contains all release changes

### 2. Create Release Tag
**Owner:** Documentation Lead

```bash
# Create annotated tag
git tag -a docs-v1.X.Z -m "Documentation release v1.X.Z

- Summary of changes
- New content areas
- Updated areas
- Ante compatibility: X.Y.Z - X.Y.x"

# Or using Git Flow
git flow release finish 1.X.Z
```

**Tag format:** `docs-vX.Y.Z` (example: `docs-v1.2.0`)

**Tag message should include:**
- Release version
- Release date
- Ante compatibility
- Summary of changes

### 3. Push Tag to Remote
**Owner:** Documentation Lead

```bash
git push origin docs-v1.X.Z
git push origin main
```

**Verify:** Tag appears on GitHub releases page

### 4. Create GitHub Release
**Owner:** Documentation Lead

On GitHub, go to Releases and:

- [ ] Select the tag you just created
- [ ] Title: `Documentation v1.X.Z`
- [ ] Copy release notes from RELEASES.md
- [ ] Include:
  - Release date
  - Ante compatibility
  - Summary
  - New content
  - Updated content
  - Breaking changes (if any)
  - Migration guide (if applicable)
- [ ] Mark as "Latest release" if applicable
- [ ] Publish release

**Release notes template:**
```
## Documentation v1.X.Z

**Release Date:** February 15, 2024  
**Compatible with:** Ante 0.4.0 - 0.5.x

### Summary
[Your summary here]

### New Content
- [List new sections]

### Updated Content
- [List updated sections]

### Migration Guide
[Include if breaking changes]

### Known Issues
[List if any]
```

### 5. Deploy Documentation
**Owner:** DevOps / Deployment Team

- [ ] Trigger documentation build/deploy pipeline
- [ ] Deploy to production
- [ ] Verify website is updated with new version
- [ ] Check version selector shows new version
- [ ] Verify `/docs/latest` points to new release

**Deployment checklist:**
- [ ] Build completes successfully
- [ ] No deployment errors
- [ ] Website loads without errors
- [ ] Latest version is live
- [ ] Version history is accessible
- [ ] Redirects work correctly

### 6. Update Version Selector
**Owner:** DevOps / Deployment Team

- [ ] Update documentation site version switcher
- [ ] Ensure old version still accessible (e.g., `/docs/v1.1.0`)
- [ ] Update `/docs/latest` redirect
- [ ] Update `/docs/v1` to point to latest v1.x.x

### 7. Announce Release
**Owner:** Documentation Lead or Communications

- [ ] Post release announcement on:
  - Changelog/blog
  - GitHub discussions
  - Slack/community channels
  - Twitter or other social media
  
**Announcement template:**
```
📚 Documentation v1.X.Z is now available!

✨ What's new:
- [New feature 1]
- [New feature 2]
- [New feature 3]

Compatible with Ante 0.4.0 - 0.5.x

Read the full release notes: [link]
```

---

## Post-Release Phase (1-7 days after release)

### 1. Monitor for Issues
**Owner:** Documentation Team

- [ ] Monitor support channels for documentation issues
- [ ] Check GitHub issues for doc bugs reported with this release
- [ ] Monitor user feedback in community channels
- [ ] Review analytics for popular pages in new release

**Duration:** First 24 hours intensively, then ongoing

**Common issues to watch for:**
- Broken links in new content
- Code examples that don't work
- Typos or formatting issues
- Navigation problems
- Search functionality issues

### 2. Handle Critical Issues
**Owner:** Documentation Lead

If critical issues found:

- [ ] Create hotfix branch: `git checkout -b hotfix/docs-v1.X.Z`
- [ ] Fix issue
- [ ] Update version to v1.X.(Z+1) - this is a patch release
- [ ] Follow Release Phase steps to deploy hotfix
- [ ] Document issue and fix in RELEASES.md

**What constitutes "critical":**
- Documentation is factually incorrect
- Code examples cause errors for users
- Important links are broken
- Navigation is broken
- Security or compliance information is wrong

**Hotfix SLA:** Deploy within 24 hours of identification

### 3. Collect Feedback
**Owner:** Documentation Team

- [ ] Create feedback survey if appropriate
- [ ] Gather user comments and suggestions
- [ ] Note common questions or confusion points
- [ ] Track areas users request more documentation on

### 4. Update Issue Tracking
**Owner:** Documentation Lead

- [ ] Close related GitHub issues
- [ ] Tag issues fixed in this release
- [ ] Create issues for feedback received
- [ ] Plan documentation improvements for next release

### 5. Update Previous Version Status
**Owner:** Documentation Lead

- [ ] Update version status if applicable
  - Move v1.(X-1) from "Active" to "Maintenance" if new major version
  - Schedule end-of-life for older versions
- [ ] Update VERSION_COMPATIBILITY.md with support timeline
- [ ] Update RELEASES.md with support dates

### 6. Generate Analytics Report
**Owner:** DevOps / Analytics

- [ ] Document page views by section
- [ ] Track search queries
- [ ] Note most accessed pages
- [ ] Identify pages with high bounce rate
- [ ] Plan improvements based on usage patterns

### 7. Close Release
**Owner:** Documentation Lead

- [ ] Mark release complete in issue tracking
- [ ] Archive any temporary release materials
- [ ] Document lessons learned
- [ ] Plan improvements for next release cycle

---

## Release Checklist

### Pre-Release Checklist (1-2 days before)
- [ ] Release notes prepared
- [ ] Release branch created
- [ ] Version references updated
- [ ] All links validated
- [ ] Code examples tested
- [ ] Grammar and spelling checked
- [ ] Ante compatibility verified
- [ ] PR created and reviewed
- [ ] All checks passing

### Release Checklist (Release day)
- [ ] Release branch merged
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Documentation deployed
- [ ] Version selector updated
- [ ] Release announced
- [ ] Monitoring activated

### Post-Release Checklist (1-7 days after)
- [ ] No critical issues identified
- [ ] Feedback collected
- [ ] Issues updated
- [ ] Previous version status updated
- [ ] Analytics reviewed
- [ ] Release closed

---

## Rollback Procedures

### Scenario: Critical Issue Found After Release

**Decision Point:** Is the issue critical enough to rollback?

**Criteria for rollback:**
- Documentation is causing widespread user confusion
- Code examples are dangerous or incorrect
- Major security/compliance information is wrong
- Website is non-functional due to release
- Multiple users report the same blocking issue

**If YES - Rollback immediately:**

```bash
# Identify the previous version tag
git tag -l docs-v* | sort -V | tail -2

# Revert to previous release
git revert <merge-commit-hash>
git tag docs-v1.X.(Z-1)-rollback
git push origin <branch>

# Redeploy from previous version
# [Deploy using same process as release]
```

**Post-rollback actions:**
- [ ] Announce rollback in community channels
- [ ] Apologize for inconvenience
- [ ] Commit to fix in v1.X.(Z+1) hotfix
- [ ] Create issue documenting problem
- [ ] Begin hotfix immediately

**If NO - Create hotfix release:**

- [ ] Create hotfix branch
- [ ] Fix issue
- [ ] Increment patch version (v1.X.(Z+1))
- [ ] Follow Release Phase to deploy
- [ ] Update RELEASES.md with hotfix note

---

## Communication During Release

### Pre-Release
- Notify team that release is planned
- Share release notes with stakeholders

### Release Day
- Announce release once live
- Share version compatibility info
- Direct users to migration guides if applicable

### Post-Release
- Monitor community feedback
- Respond to questions about new features
- Document common issues and solutions

---

## Troubleshooting

### Issue: Build fails during deployment
**Solution:** Check build logs, fix issue, create new tag with incremented patch version

### Issue: Broken links discovered after release
**Solution:** Fix immediately with hotfix release (v1.X.Z+1)

### Issue: Code examples don't work with target Ante version
**Solution:** Rollback or create immediate hotfix with corrected examples

### Issue: Version selector not updating
**Solution:** Clear cache, manually trigger deployment, verify configuration

---

## Related Documents

- **VERSIONING.md** - Version numbering strategy
- **RELEASES.md** - Release history and notes
- **VERSION_COMPATIBILITY.md** - Ante compatibility details
- **CHANGELOG_TEMPLATE.md** - How to format changelog entries
