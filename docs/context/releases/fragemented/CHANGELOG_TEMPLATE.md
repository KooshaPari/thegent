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
