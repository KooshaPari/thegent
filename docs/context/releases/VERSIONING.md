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
