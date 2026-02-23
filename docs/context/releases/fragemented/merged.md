# Merged Fragmented Markdown

## Source: docs/context/releases

## Source: CHANGELOG_TEMPLATE.md

# Changelog Template

## Overview

This template is used for creating changelog entries for documentation releases. Use this format for both:
- Individual changelog files (per release or per component)
- The RELEASES.md file entries
- GitHub release notes

---

## Changelog Entry Format

### Full Release Changelog

```markdown
## [Version Number] - Release Date

### Added
- **Feature/Section Name**: Brief description of what was added
  - Subsection or related item
  - Another related item
- **Another Feature**: Description
  - Details about the feature
  
### Changed
- **Section Name**: What changed and why
  - Impact of the change
  - Migration notes if needed
- **Another Change**: Description of change

### Fixed
- Fixed broken link in [Section Name]
- Corrected code example in [Page Name]
- Resolved formatting issue in [Component]

### Deprecated
- **Feature Name**: Explanation of deprecation, replacement approach
  - Timeline for removal
  - How to migrate to new approach
- **Another Feature**: Details

### Removed
- Removed deprecated [Feature Name]
  - Explanation of why
  - Where to find replacement content
- Removed [Old Section]

### Security
- Updated security guidance for [topic]
- Added warnings about [security issue]
```

---

## Real-World Example

### 1.2.0 - February 15, 2024

#### Added
- **Plugin Development Guide**: Complete guide to building and publishing Ante plugins
  - Plugin architecture and lifecycle documentation
  - Plugin configuration and metadata reference
  - Testing and debugging plugins guide
  - Publishing to plugin registry instructions
- **Advanced CLI Usage**: Deep dive into command-line features
  - Shell integration and completion setup
  - Scripting with Ante CLI
  - Custom aliases and workflow examples
- **Troubleshooting Guide**: Common issues and solutions
  - Performance optimization tips
  - Error message reference
  - FAQ section for common problems

#### Changed
- **Getting Started Guide**: 
  - Clearer prerequisites section
  - Improved workflow examples
  - Added more screenshots and diagrams
- **API Reference**: 
  - Added TypeScript examples alongside JavaScript
  - Improved parameter descriptions
  - Added more real-world use cases
- **Configuration Guide**: 
  - Expanded environment variable reference
  - Added examples for all configuration options
  - Improved organization and navigation

#### Fixed
- Fixed broken links to external resources in Security Best Practices
- Corrected outdated code examples in Webhook documentation
- Resolved formatting issues in API response tables
- Fixed typos in Configuration guide

#### Deprecated
- **Deprecated:** `--experimental-flag` in CLI documentation
  - Use `--feature-flag` instead (available in Ante 0.4.0+)
  - Will be removed in documentation v2.0.0
  - See [migration guide](#) for details

#### Removed
- Removed legacy authentication methods documentation
  - Content moved to [v1.1.0 archive](/docs/v1.1.0)
  - New authentication guide available in Getting Started
  - See migration guide for upgrading authentication

#### Security
- Updated security best practices for Ante 0.5.x
- Added warnings about deprecated encryption methods
- Enhanced API key security recommendations

---

## Component-Specific Changelog

Use this format for documenting changes to specific documentation sections:

```markdown
### Getting Started Guide

#### Added
- New section: "Before You Start" with prerequisites
- Step-by-step video walkthrough (embedded)
- Common setup issues and solutions

#### Changed
- Restructured prerequisites for clarity
- Updated installation instructions for Ante 0.4.x
- Improved example project walkthrough

#### Fixed
- Corrected npm package name in installation step
- Fixed broken link to sample repository
- Updated outdated version numbers

---

### API Reference

#### Added
- TypeScript examples for all major endpoints
- Error response documentation for each endpoint
- Rate limiting information

#### Changed
- Reorganized endpoints by resource type
- Improved parameter descriptions
- Added more context about response formats

#### Fixed
- Corrected response format examples
- Fixed incorrect parameter types
- Updated deprecated endpoints information
```

---

## Changelog Entry Guidelines

### General Rules

1. **Be Specific**: Use clear section names and descriptions
   ```markdown
   ✅ Good:   "Added Plugin Development Guide with architecture overview"
   ❌ Bad:    "Added new documentation"
   ```

2. **Use Active Voice**: Make it clear who is doing what
   ```markdown
   ✅ Good:   "Added TypeScript examples to API reference"
   ❌ Bad:    "TypeScript examples were added"
   ```

3. **Explain the Impact**: Why is this change important?
   ```markdown
   ✅ Good:   "Expanded configuration guide with environment variables
              (users can now set options without config files)"
   ❌ Bad:    "Expanded configuration guide"
   ```

4. **Include Context**: Link to related content or explain context
   ```markdown
   ✅ Good:   "Fixed code examples in Webhook guide (now works with Ante 0.4.x)"
   ❌ Bad:    "Fixed code examples"
   ```

### For Each Section

#### Added
- Describe what's new
- Mention what content areas it covers
- Explain why it was added
- Link to the new content if possible

**Template:**
```
- **[Name of New Section/Feature]**: [Brief description of what it covers]
  - [Subsection or key topic]
  - [Another key topic]
```

#### Changed
- Explain what was modified
- Describe the change
- Note if it affects user experience
- Include migration notes if needed

**Template:**
```
- **[Section Name]**: [What changed and why]
  - [Specific change detail]
  - [Impact or note about the change]
```

#### Fixed
- Be specific about what was broken
- Explain the fix
- Mention if this affects current users
- Provide workaround if applicable

**Template:**
```
- Fixed [specific issue] in [location]
  - [What was wrong]
  - [What was fixed]
```

#### Deprecated
- Clearly state what's deprecated
- Explain why it's deprecated
- Provide replacement or migration path
- Set clear timeline for removal

**Template:**
```
- **[Feature Name]**: [Why it's deprecated]
  - Replacement: [New approach or feature]
  - Timeline: Will be removed in [version/date]
  - Migration: See [link to migration guide]
```

#### Removed
- State what was removed
- Explain why
- Point to archived versions if needed
- Provide migration/replacement information

**Template:**
```
- Removed [feature/section]
  - Reason: [Why it was removed]
  - Replacement: [New approach]
  - Archive: Available in [previous version]
```

#### Security
- Be clear about the security implication
- Provide actionable guidance
- Link to security guidelines
- Include timeline if urgent

**Template:**
```
- [Security issue fix or guidance]
  - Impact: [What was at risk]
  - Action: [What users should do]
  - Reference: [Link to security guide]
```

---

## Examples by Change Type

### Example 1: New Section Added

**Poor:**
```markdown
Added documentation about plugins
```

**Good:**
```markdown
- **Plugin Development Guide**: Comprehensive guide to building, testing, and 
  publishing Ante plugins
  - Plugin architecture and lifecycle
  - Configuration and metadata requirements
  - Testing and debugging procedures
  - Publishing to plugin registry
```

**Excellent:**
```markdown
- **Plugin Development Guide**: Complete guide for building production-ready 
  Ante plugins, enabling users to extend Ante functionality
  - Plugin architecture overview and lifecycle hooks
  - Plugin configuration with JSON schema and validation
  - Testing strategies including unit and integration tests
  - Step-by-step publishing guide to official registry
  - Examples for common plugin patterns (middleware, integrations, extensions)
```

---

### Example 2: Content Updated

**Poor:**
```markdown
Updated API reference
```

**Good:**
```markdown
- **API Reference**: Added TypeScript examples and improved parameter descriptions
  - TypeScript type definitions for all endpoints
  - Enhanced parameter documentation
  - More detailed response format descriptions
```

**Excellent:**
```markdown
- **API Reference**: Enhanced with TypeScript examples and comprehensive error 
  documentation for better developer experience
  - TypeScript type definitions and JSDoc comments for all 45+ endpoints
  - Detailed error response documentation including error codes and recovery steps
  - Real-world code examples showing common patterns and best practices
  - Interactive API playground (links to live documentation)
```

---

### Example 3: Bug Fixed

**Poor:**
```markdown
Fixed code examples
```

**Good:**
```markdown
- Fixed outdated code examples in Webhook guide
  - Examples now work with Ante 0.4.x API
  - Updated deprecated method calls
```

**Excellent:**
```markdown
- Fixed code examples in Webhook Integration guide that were causing 
  "TypeError" for Ante 0.4.x+ users
  - Updated deprecated `webhook.on()` calls to `webhook.listen()`
  - Corrected request body structure to match current API
  - Verified all examples execute successfully against Ante 0.4.0+
  - Added version notes indicating which examples apply to which Ante versions
```

---

### Example 4: Deprecation Notice

**Poor:**
```markdown
Deprecated old authentication method
```

**Good:**
```markdown
- **Deprecated**: Old authentication method
  - Use new OAuth2 approach instead
  - Will be removed in v2.0.0
```

**Excellent:**
```markdown
- **Deprecated**: Legacy API key authentication in Custom Authentication guide
  - Reason: OAuth2 provides better security and scope management
  - Replacement: Migrate to OAuth2 using provided migration guide
  - Timeline: Supported until documentation v2.0.0 (estimated Q3 2024)
  - Migration: See [Authentication Migration Guide](../guides/auth-migration.md)
  - Impact: Only affects apps using legacy API key auth; OAuth2 users unaffected
```

---

## Changelog for RELEASES.md

When adding to RELEASES.md, use this condensed format:

```markdown
### 1.3.0
**Released:** [Date]  
**Compatible with:** Ante X.Y.Z - X.Y.x  
**Current Status:** Active

#### Summary of Changes
Added advanced features documentation, expanded API reference with TypeScript 
support, and improved troubleshooting guides based on user feedback.

#### New Content Areas
- **Advanced Configuration**: Configuration automation and complex setups
  - Environment variable orchestration
  - Configuration validation and schemas
  - Multi-environment setup patterns
- **Performance Guide**: Optimization strategies and best practices
  - Benchmarking guide
  - Common performance bottlenecks
  - Optimization techniques

#### Updated Content Areas
- Getting Started guide - enhanced with advanced scenarios
- CLI Reference - added shell integration examples
- Security Best Practices - updated for Ante X.Y features

#### Deprecated/Removed Content
- Deprecated: Old configuration format (use new JSON format)
  - Timeline: Will be removed in v2.0.0
  - Migration: See migration guide

#### Known Issues
- Advanced Configuration examples assume Unix-like environment
```

---

## Checklist for Creating Changelog Entries

- [ ] Reviewed all changes since last release
- [ ] Categorized changes into appropriate sections (Added, Changed, Fixed, etc.)
- [ ] Used specific, descriptive language
- [ ] Used active voice
- [ ] Included context and impact for each entry
- [ ] Linked to related documentation where relevant
- [ ] Included version compatibility information
- [ ] Verified spelling and grammar
- [ ] Checked that deprecations have clear migration paths
- [ ] Confirmed all references are accurate
- [ ] Updated RELEASES.md file
- [ ] Created GitHub release notes from changelog

---

## Tools and Automation

### Automated Changelog Generation

If using git-based changelog generation:

```bash
# Using conventional commits to generate changelog
npx conventional-changelog-cli -p angular -i CHANGELOG.md -s

# Using commitizen for structured commits
npm install -g commitizen

# Create a commit with changelog information
cz commit
```

### Manual Process

1. Review git log between release tags
2. Group commits by type (feat, fix, refactor, etc.)
3. Format according to this template
4. Review for clarity and completeness
5. Update RELEASES.md

---

## Related Documents

- **RELEASES.md** - Full release history
- **VERSIONING.md** - Versioning strategy
- **RELEASE_PROCESS.md** - How to create releases
- **VERSION_COMPATIBILITY.md** - Version compatibility details


---

## Source: RELEASES.md

# Documentation Release History

## Active Releases

### 1.2.0
**Released:** February 15, 2024  
**Compatible with:** Ante 0.4.0 - 0.5.x  
**Current Status:** Active - Latest Release

#### Summary of Changes
Added comprehensive plugin development guide, improved API reference documentation, and expanded CLI command documentation with real-world examples.

#### New Content Areas
- **Plugin Development Guide** - Complete guide to building and publishing Ante plugins
  - Plugin architecture and lifecycle
  - Plugin configuration and metadata
  - Testing and debugging plugins
  - Publishing to plugin registry
- **Advanced CLI Usage** - Deep dive into command-line features
  - Shell integration and completion
  - Scripting with Ante CLI
  - Custom aliases and workflows
- **Troubleshooting Guide** - Common issues and solutions
  - Performance optimization tips
  - Error message reference
  - FAQ section

#### Updated Content Areas
- Getting Started guide - clearer prerequisites and improved workflow examples
- API Reference - added TypeScript examples alongside JavaScript
- Configuration Guide - expanded environment variable reference
- Security Best Practices - updated with new Ante 0.5.x features

#### Deprecated/Removed Content
- Removed deprecated `--experimental-flag` documentation
- Moved legacy authentication methods to migration guide

#### Migration Guide
- No breaking changes from v1.1.x
- New plugin development content is additive
- All existing links and navigation remain unchanged
- Users on v1.1.x can upgrade without any configuration changes

#### Known Issues
- Plugin registry integration examples may need adjustment if using older Node versions
- Some advanced shell integration features require bash/zsh 5.0+

---

### 1.1.0
**Released:** December 8, 2023  
**Compatible with:** Ante 0.3.0 - 0.4.x  
**Current Status:** Maintenance

#### Summary of Changes
Introduced new Configuration Guide section, expanded API documentation with examples, and improved quickstart walkthrough.

#### New Content Areas
- **Configuration Guide** - How to configure Ante
  - Configuration file formats (JSON, YAML)
  - Environment variables
  - Command-line overrides
  - Configuration inheritance and precedence
- **API Examples** - Real-world usage patterns
  - Common workflows
  - Integration examples
  - Error handling patterns
  - Performance considerations

#### Updated Content Areas
- Getting Started - enhanced with configuration examples
- CLI Reference - added practical usage examples
- Architecture Overview - clarified component interactions

#### Deprecated/Removed Content
- None - full backward compatibility maintained

#### Migration Guide
- N/A - fully backward compatible with v1.0.x

#### Known Issues
- Configuration guide examples assume Unix-like environment
- Some YAML examples need escaping adjustments on Windows

---

### 1.0.0
**Released:** September 20, 2023  
**Compatible with:** Ante 0.2.0 - 0.3.x  
**Current Status:** End-of-Life (June 20, 2024)

#### Summary of Changes
Initial documentation release covering core Ante features, installation, basic usage, and API reference.

#### Content Coverage
- Installation and Setup
- Quick Start Guide
- Core Concepts
- CLI Command Reference
- Configuration Reference
- Basic API Documentation
- Troubleshooting

#### Known Limitations
- Limited plugin documentation
- Basic API examples only
- No advanced configuration examples
- Missing performance optimization guides

#### End-of-Life Timeline
- Maintenance ended: June 20, 2024
- Archive available at: `/docs/v1.0.0`
- Users should migrate to v1.1.0 or later

---

## Release Template

For future releases, use this template:

```markdown
### X.Y.Z
**Released:** [Date]  
**Compatible with:** Ante [version range]  
**Current Status:** [Active / Maintenance / End-of-Life]

#### Summary of Changes
[2-3 sentence overview of major changes in this release]

#### New Content Areas
- **Section Name** - Brief description
  - Subtopic 1
  - Subtopic 2
  - Subtopic 3

#### Updated Content Areas
- Content area 1 - what changed
- Content area 2 - what changed
- Content area 3 - what changed

#### Deprecated/Removed Content
- What was removed and why
- Replacement or migration path

#### Breaking Changes
- List any breaking changes
- Impact assessment
- Migration requirements

#### Migration Guide
- Step-by-step instructions if applicable
- Updated procedures or URLs
- Configuration changes needed

#### Known Issues
- Any known limitations or issues
- Workarounds if available
- When issue will be fixed
```

## Release Statistics

| Version | Release Date | Ante Compatibility | Days in Active | Content Files |
|---------|-------------|-------------------|----------------|--------------|
| 1.2.0 | Feb 15, 2024 | 0.4.0 - 0.5.x | Active | 47 |
| 1.1.0 | Dec 8, 2023 | 0.3.0 - 0.4.x | 69 days | 42 |
| 1.0.0 | Sep 20, 2023 | 0.2.0 - 0.3.x | 273 days | 35 |

## How to Find Specific Versions

**Current/Latest Documentation:**
- Website: `/docs` or `/docs/latest`
- GitHub: `main` branch

**Specific Version (e.g., 1.1.0):**
- Website: `/docs/v1.1.0`
- GitHub: Tag `docs-v1.1.0`

**Latest in Major Version (e.g., v1.x.x):**
- Website: `/docs/v1`

**Archived Versions:**
- Full archive: `/docs/archive`
- All versions remain available indefinitely

## Support Matrix

| Version | Ante Compatibility | Support Level | Ends |
|---------|-------------------|---------------|------|
| 1.2.0 | 0.4.0 - 0.5.x | Active | TBD |
| 1.1.0 | 0.3.0 - 0.4.x | Maintenance | 2024-09-15 |
| 1.0.0 | 0.2.0 - 0.3.x | End-of-Life | 2024-06-20 |

## Changelog by Component

### Getting Started
- v1.2.0: Improved examples and clearer prerequisites
- v1.1.0: Enhanced with configuration introduction
- v1.0.0: Initial version

### API Reference
- v1.2.0: Added TypeScript examples, improved structure
- v1.1.0: Initial comprehensive API documentation with examples
- v1.0.0: Basic API reference only

### CLI Reference
- v1.2.0: Advanced usage guide added
- v1.1.0: Enhanced with practical examples
- v1.0.0: Basic command reference

### Configuration
- v1.2.0: Environment variables expanded
- v1.1.0: Initial configuration guide
- v1.0.0: Basic configuration reference included in API docs

## Related Documents

- **VERSIONING.md** - Version numbering strategy and guidelines
- **RELEASE_PROCESS.md** - How to create new releases
- **VERSION_COMPATIBILITY.md** - Ante version compatibility details
- **CHANGELOG_TEMPLATE.md** - Template for creating changelog entries


---

## Source: RELEASE_PROCESS.md

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


---

## Source: VERSIONING.md

# Documentation Versioning Strategy

## Overview

The Ante documentation uses semantic versioning independent from Ante product releases. This allows documentation to evolve on its own release cadence while maintaining clear compatibility information with specific Ante versions.

## Version Numbering Scheme

Documentation versions follow **MAJOR.MINOR.PATCH** format:

```
MAJOR.MINOR.PATCH
  |     |      └─ Patch releases (bug fixes, minor corrections)
  |     └─────── Minor releases (new content, improvements, non-breaking changes)
  └──────────── Major releases (major content restructuring, breaking documentation changes)
```

**Example versions:**
- `1.0.0` - Initial release
- `1.1.0` - New content sections added
- `1.2.3` - Multiple patch fixes
- `2.0.0` - Major restructuring or breaking changes

## When to Bump Each Version

### PATCH (1.0.X → 1.0.Y)
Increment patch version when:
- Fixing typos, grammar, or clarity issues
- Correcting outdated code examples
- Updating URLs or references
- Improving formatting without structural changes
- Adding clarifications to existing content
- Fixing broken links or references

**Release frequency:** As needed, usually batched weekly

### MINOR (1.X.0 → 1.Y.0)
Increment minor version when:
- Adding new documentation sections or guides
- Expanding existing topics with substantial new content
- Adding new code examples or use cases
- Improving documentation structure (within a major section)
- Adding new features documentation that aligns with Ante releases
- Introducing new reference materials or appendices

**Requirements:**
- All content is backward compatible
- Existing links and references still work
- No content is removed or restructured significantly
- Search and navigation still function correctly

**Release frequency:** Every 2-4 weeks during active development

### MAJOR (X.0.0 → Y.0.0)
Increment major version when:
- Restructuring documentation organization
- Renaming or moving major sections
- Removing outdated content or sections
- Changing documentation conventions or terminology significantly
- Making navigation or information architecture changes
- Breaking existing documentation references or URLs

**Requirements:**
- Migration guide provided
- Clear deprecation timeline for old version
- Updated version compatibility matrix
- Communication plan for users

**Release frequency:** Quarterly or as needed

## Release Types

### Regular Release
Standard release containing documentation improvements and new content.

**Trigger:**
- Accumulation of 5+ meaningful changes
- New Ante feature release
- Scheduled release cycle

### Minor Release
Small, targeted release with limited scope.

**Trigger:**
- Critical corrections needed urgently
- Single important feature documentation
- Time-sensitive content updates

### Hotfix Release
Immediate patch release for critical errors.

**Trigger:**
- Documentation is incorrect and misleading
- Links are broken in critical paths
- Examples cause user issues
- Security or compliance information is wrong

**Timeline:** Released within 24 hours of identification

## Compatibility Guarantees

### Backward Compatibility
- Documentation versions maintain content compatibility within major versions
- URLs should not change within a major version (URL redirects acceptable)
- Navigation structure remains consistent
- Code examples remain valid for documented Ante versions

### Forward Compatibility
- Documentation for an Ante version is usable with newer Ante versions when relevant
- Feature documentation applies to all subsequent versions unless explicitly versioned
- Breaking changes in Ante trigger major documentation updates

### Cross-Version Access
- Users on older Ante versions can access documentation from earlier doc versions
- Version selector allows switching between documentation versions
- All documentation versions remain published and accessible

## How to Reference Specific Versions

### In URLs
```
/docs/v1.2.0/getting-started
/docs/latest/getting-started
/docs/v1/getting-started  (points to latest v1.x.x)
```

### In Code/Tools
```
ante-docs-v1.2.0
"documentation version": "1.2.0"
```

### In Content
```
**Documentation version:** 1.2.0 (compatible with Ante 0.4.x - 0.5.x)
**See also:** [Getting Started v1.1.0](/docs/v1.1.0/getting-started)
```

### In Metadata (Front matter)
```yaml
---
version: 1.2.0
released: 2024-06-15
ante_version: "0.4.0-0.5.x"
prev_version: 1.1.0
next_version: 1.3.0
---
```

## Version Lifecycle

### Active
- Current major version in development
- Previous major version (one release back)
- Receives updates, bug fixes, and new content
- Full support and maintenance

### Maintenance
- One major version before Active
- Receives critical hotfixes only
- Supported for 6 months from next major release
- No new features or improvements

### End-of-Life
- Older major versions
- No updates or support
- Archives available for reference
- Community can submit PRs if critical

## Deprecated Features

When deprecating documentation sections or moving content:

1. **Deprecation Phase (1 minor version)**
   - Keep old content
   - Add deprecation notice at top
   - Link to replacement content
   - Example: "This approach is deprecated in favor of [new method]"

2. **Migration Phase (1 minor version)**
   - Maintain both versions
   - Provide migration guide
   - Update related links and references
   - Gather feedback

3. **Removal Phase (next major version)**
   - Remove deprecated content
   - Update all references
   - Document in migration guide
   - Archive in version history

## Version Numbering Examples

| Change | Current | New | Type |
|--------|---------|-----|------|
| Fix typo in CLI guide | 1.5.0 | 1.5.1 | Patch |
| Add new guide section | 1.5.1 | 1.6.0 | Minor |
| Add 3 new tutorials | 1.6.0 | 1.7.0 | Minor |
| Restructure navigation | 1.7.0 | 2.0.0 | Major |
| Hotfix broken example | 1.5.0 | 1.5.1 | Patch |

## Related Documents

- **RELEASES.md** - Release history and notes
- **RELEASE_PROCESS.md** - How to execute releases
- **VERSION_COMPATIBILITY.md** - Ante version compatibility matrix
- **GOVERNANCE.md** - Documentation governance (parent document)


---

## Source: VERSION_COMPATIBILITY.md

# Documentation and Ante Version Compatibility

## Overview

This document maps documentation versions to Ante product versions, showing which documentation is compatible with which Ante releases.

The Ante documentation is versioned independently from the Ante product to allow for more flexible documentation updates. However, each documentation version targets specific Ante versions.

## Compatibility Matrix

### Documentation v1.2.0 (Current)
| Aspect | Details |
|--------|---------|
| **Documentation Version** | 1.2.0 |
| **Release Date** | February 15, 2024 |
| **Status** | ✅ Active |
| **Ante Versions** | 0.4.0, 0.4.1, 0.4.x, 0.5.0, 0.5.x |
| **Node.js** | 14.0.0+ (16.0.0+ recommended) |
| **Browsers** | Modern browsers (Chrome, Firefox, Safari, Edge) |
| **Support Until** | TBD (active development) |

**What's covered:**
- Full feature documentation for Ante 0.4.x
- New features in Ante 0.5.x
- Plugin development system
- Advanced CLI usage
- Comprehensive API reference

**Version-specific sections:**
- CLI commands for 0.4.x and 0.5.x shown with version badges
- Features marked with when they were introduced
- Deprecations noted with target removal versions

---

### Documentation v1.1.0 (Maintenance)
| Aspect | Details |
|--------|---------|
| **Documentation Version** | 1.1.0 |
| **Release Date** | December 8, 2023 |
| **Status** | 🔧 Maintenance |
| **Ante Versions** | 0.3.0, 0.3.1, 0.3.x, 0.4.0, 0.4.x |
| **Node.js** | 14.0.0+ |
| **Browsers** | Modern browsers |
| **Support Until** | September 15, 2024 |

**What's covered:**
- Core Ante features stable in 0.3.x
- Configuration guide
- API documentation with examples
- CLI reference

**Not covered:**
- Plugin system (new in Ante 0.5.x)
- Advanced features from 0.5.x
- New CLI commands added in 0.5.x

**Migration path:** [Upgrade to v1.2.0](./RELEASES.md#120-february-15-2024)

---

### Documentation v1.0.0 (End-of-Life)
| Aspect | Details |
|--------|---------|
| **Documentation Version** | 1.0.0 |
| **Release Date** | September 20, 2023 |
| **Status** | ⛔ End-of-Life |
| **Ante Versions** | 0.2.0, 0.2.1, 0.2.x, 0.3.0, 0.3.x |
| **Node.js** | 12.0.0+ |
| **Browsers** | Modern browsers |
| **Support Until** | June 20, 2024 |

**What's covered:**
- Basic Ante installation and setup
- Core CLI commands
- Simple API usage
- Configuration basics

**Not covered:**
- Configuration guide details
- Advanced API patterns
- Troubleshooting guide
- Modern best practices

**Archive location:** `/docs/v1.0.0`

**Migration path:** [Upgrade to v1.1.0](./RELEASES.md#110-december-8-2023) → [v1.2.0](./RELEASES.md#120-february-15-2024)

---

## Feature Availability by Ante Version

### Feature Presence Matrix

| Feature | Ante 0.2.x | Ante 0.3.x | Ante 0.4.x | Ante 0.5.x | Doc v1.0 | Doc v1.1 | Doc v1.2 |
|---------|-----------|-----------|-----------|-----------|----------|----------|----------|
| Basic CLI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Configuration | ⚠️ Limited | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| API Reference | ⚠️ Basic | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Plugin System | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Advanced CLI | ❌ | ⚠️ Partial | ✅ | ✅ | ❌ | ❌ | ✅ |
| Troubleshooting | ❌ | ⚠️ Basic | ✅ | ✅ | ❌ | ⚠️ Partial | ✅ |
| Security Guide | ❌ | ❌ | ⚠️ Basic | ✅ | ❌ | ❌ | ✅ |

Legend: ✅ Fully supported | ⚠️ Partially supported | ❌ Not available

---

## Known Compatibility Issues

### Issue: Plugin examples require Ante 0.5.x
- **Affected:** Documentation v1.2.0 plugin examples
- **Ante versions:** 0.4.x and earlier
- **Workaround:** Use v1.1.0 documentation or upgrade to Ante 0.5.x
- **Timeline:** Fixed in Ante 0.5.0+ (released Feb 1, 2024)

### Issue: CLI command flags differ between versions
- **Affected:** CLI reference in v1.1.0 and v1.2.0
- **Ante versions:** Flags added/changed from 0.3.x to 0.4.x
- **Workaround:** Check `ante --help` for your specific version
- **Details:**
  - `--config-file` flag added in 0.4.0
  - `--verbose` changed to `--debug` in 0.5.0
  - `--dry-run` removed in 0.5.0 (use `--no-apply` instead)

### Issue: Configuration format changed in 0.5.0
- **Affected:** Configuration guide in v1.0.0 and v1.1.0
- **Ante versions:** 0.5.0+ require new JSON format
- **Workaround:** Use v1.2.0 documentation
- **Migration:** See [configuration migration guide](../guides/MIGRATION_0.4_TO_0.5.md)

---

## Upgrade Paths

### From Ante 0.2.x
```
Documentation v1.0.0 (0.2.x)
         ↓ Upgrade Ante to 0.3.x
Documentation v1.1.0 (0.3.x - 0.4.x) 
         ↓ Upgrade Ante to 0.5.x
Documentation v1.2.0 (0.4.x - 0.5.x)
```

### From Ante 0.3.x
```
Documentation v1.0.0 or v1.1.0 (0.3.x)
         ↓ Upgrade Ante to 0.4.x
Documentation v1.1.0 or v1.2.0 (0.4.x)
         ↓ (Optional) Upgrade to v1.2.0 docs
Documentation v1.2.0 (latest)
```

### From Ante 0.4.x
```
Documentation v1.1.0 or v1.2.0 (0.4.x)
         ↓ Upgrade Ante to 0.5.x (recommended)
Documentation v1.2.0 (0.5.x)
```

### From Ante 0.5.x (Latest)
```
Documentation v1.2.0 (0.5.x) ← You are here
       Stay current with updates
```

---

## Deprecation Timeline

### Documentation v1.1.0
- **Status:** Maintenance mode
- **Support until:** September 15, 2024 (6 months from v1.2.0 release)
- **Recommendations:**
  - Users on Ante 0.3.x should consider upgrading to 0.4.x
  - Users on Ante 0.4.x should upgrade docs to v1.2.0
  - Archive will remain available at `/docs/v1.1.0`
- **Removal:** No earlier than 6 months after end of support

### Documentation v1.0.0
- **Status:** End-of-Life (as of June 20, 2024)
- **Support until:** June 20, 2024 (ended)
- **Recommendations:**
  - Migrate to v1.1.0 minimum
  - Preferred migration path: v1.2.0
  - Archive available at `/docs/v1.0.0`
- **Removal:** Will remain archived indefinitely

---

## Compatibility with Development Versions

### Ante Main Branch (Development)
Documentation may lag behind main branch development. For latest features in development:

- Reference: [Ante GitHub main branch](https://github.com/AntigmaLabs/ante)
- Docs location: Check `/docs/main` or development documentation
- Status: May be unstable and incomplete
- Support: Community support only

---

## Accessing Different Documentation Versions

### Online
```
Latest (v1.2.0):
https://docs.antigma.ai/docs
https://docs.antigma.ai/docs/latest

Specific version:
https://docs.antigma.ai/docs/v1.2.0
https://docs.antigma.ai/docs/v1.1.0
https://docs.antigma.ai/docs/v1.0.0

Latest in major version:
https://docs.antigma.ai/docs/v1

Archive:
https://docs.antigma.ai/docs/archive
```

### Local Installation
If documentation is included with Ante:

```bash
# View current version's docs
ante docs

# View specific version (if available locally)
ante docs --version 1.1.0

# View in browser
ante docs --browser
```

### GitHub
```bash
# Clone specific version
git clone --branch docs-v1.2.0 https://github.com/AntigmaLabs/ante.git docs-v1.2.0

# View releases
https://github.com/AntigmaLabs/ante/releases
```

---

## Choosing Your Documentation Version

### Checklist: Which documentation version should I use?

1. **What version of Ante are you running?**
   - 0.5.x → Use Documentation v1.2.0 ✅
   - 0.4.x → Use Documentation v1.2.0 ✅
   - 0.3.x → Use Documentation v1.1.0 ✅
   - 0.2.x → Use Documentation v1.0.0 (consider upgrading)

2. **Do you need plugin documentation?**
   - Yes → Documentation v1.2.0 required (0.5.0+ only)
   - No → Your version's documentation is fine

3. **Are you experiencing issues with examples?**
   - Yes → Check this compatibility matrix for known issues
   - No → Continue with your current version

4. **Do you want latest features and best practices?**
   - Yes → Upgrade Ante to latest and use Documentation v1.2.0
   - No → Your current version works fine

---

## Version Support Lifecycle

### Timeline
```
Release Date         Mar 2023  Jun 2023  Sep 2023  Dec 2023  Feb 2024
                       |        |         |         |         |
Doc Version:        v1.0 ───────────────────────────────────→ EOL
                                      ↓
                                    v1.1 ────────────────────→ v1.2
                                                    ↓
                                                  v1.2 (Current)
                                                     ↓
                                              Active Development
```

### Support Levels by Version
| Version | Status | Support | Updates | Archive |
|---------|--------|---------|---------|---------|
| v1.2.x | Active | Full | Yes | Yes |
| v1.1.x | Maintenance | Limited | Hotfixes only | Yes |
| v1.0.x | EOL | None | None | Yes |

---

## Related Documents

- **VERSIONING.md** - How versions are numbered and managed
- **RELEASES.md** - Release history and notes
- **RELEASE_PROCESS.md** - How to create new releases
- **CHANGELOG_TEMPLATE.md** - How to format changelog entries


---

Copied count: 5