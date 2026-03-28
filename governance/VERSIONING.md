# Phenotype Versioning Strategy

## Overview

This document defines the versioning strategy for all Phenotype packages and libraries.

## Versioning Model

### Semantic Versioning (SemVer)

All Phenotype packages follow **Semantic Versioning 2.0.0**:

```
MAJOR.MINOR.PATCH
     |     |     |
     |     |     +-- Patch: Bug fixes, no API changes
     |     +-------- Minor: New features, backward compatible
     +-------------- Major: Breaking changes
```

### Pre-release Versions

```
MAJOR.MINOR.PATCH-prerelease
1.0.0-alpha.1      # Alpha release
1.0.0-beta.2       # Beta release
1.0.0-rc.1         # Release candidate
```

## Package Types

### Type A: Phenotype-Domain Packages (`packages/`)

**Prefix:** `@phenotype/`

| Package | Version | Status |
|--------|---------|--------|
| `phenotype-config` | 0.x | Alpha |
| `phenotype-design` | 0.x | Alpha |
| `phenotype-agent` | 0.x | Alpha |
| `phenotype-task` | 0.x | Alpha |
| `phenotype-research` | 0.x | Alpha |
| `phenotype-docs` | 0.x | Alpha |

**Policy:**
- Start at `0.1.0`
- Increment minor for new features
- Increment patch for bug fixes
- Move to `1.0.0` when stable
- Major version bump for breaking changes

### Type B: Extractable Libraries (`libs/`)

**No Phenotype prefix** - standalone library names

| Library | Version | Status |
|--------|---------|--------|
| `hexagonal-rs` | 0.x | Alpha |
| `hexagonal-ts` | 0.x | Alpha |
| `hexagonal-py` | 0.x | Alpha |
| `hexagonal-go` | 0.x | Alpha |
| `xdd-lib-rs` | 0.x | Alpha |
| `event-sourcing` | 0.x | Alpha |
| `state-machine` | 0.x | Alpha |

**Policy:**
- More aggressive versioning allowed
- Can start at `0.0.1`
- Target `1.0.0` within 6 months
- Breaking changes allowed in `0.x`

## Release Process

### Release Stages

1. **Development** (`0.x.y-dev`)
   - Active development
   - API unstable
   - No guarantee of stability

2. **Alpha** (`0.x.y-alpha.z`)
   - Feature complete
   - Known bugs exist
   - API may change

3. **Beta** (`0.x.y-beta.z`)
   - All features implemented
   - Known bugs being fixed
   - API stabilizing

4. **Release Candidate** (`0.x.y-rc.z`)
   - Release candidate
   - No known bugs
   - API frozen for review

5. **Stable** (`1.x.y` or `0.x.y`)
   - Production ready
   - Semantic versioning applies
   - Breaking changes = major bump

### Release Frequency

| Package Type | Target Frequency |
|-------------|------------------|
| Phenotype-domain (`packages/`) | Monthly |
| Libraries (`libs/`) | Bi-weekly |
| Infrastructure | As needed |

## Changelog Format

All packages must maintain a `CHANGELOG.md`:

```markdown
# Changelog

## [1.2.3] - 2026-03-25

### Added
- New feature X
- New API endpoint Y

### Changed
- Updated dependency Z
- Improved performance

### Deprecated
- Old function A (use B instead)

### Removed
- Removed deprecated function C

### Fixed
- Bug in function D

### Security
- Vulnerability in E (CVE-XXXX-XXXX)
```

## Publishing

### Rust (crates.io)

```bash
# Dry run first
cargo publish --dry-run

# Publish
cargo publish

# Tag
git tag v1.2.3
git push origin v1.2.3
```

### JavaScript/TypeScript (npm)

```bash
# Build
npm run build

# Dry run
npm publish --dry-run

# Publish (public)
npm publish --access public

# Tag version
npm version minor
git push && git push --tags
```

### Python (PyPI)

```bash
# Build
python -m build

# Upload
twine upload dist/*
```

### Go (GitHub Packages)

```bash
# Tag
git tag v1.2.3
git push origin v1.2.3
```

## Deprecation Policy

### Deprecation Process

1. Add deprecation notice in code
2. Document in CHANGELOG
3. Set sunset date (minimum 3 months)
4. Remove in next major version

### Deprecation Notice Format

```rust
#[deprecated(since = "1.2.0", note = "Use new_function instead")]
pub fn old_function() { }

#[deprecated(since = "1.2.0", note = "Use NewStruct instead")]
pub struct OldStruct { }
```

```typescript
/**
 * @deprecated since 1.2.0, use newFunction instead
 */
export function oldFunction() { }
```

## Breaking Changes

### What Constitutes Breaking

| Change Type | Breaking? |
|------------|-----------|
| Function signature change | Yes |
| Removed function | Yes |
| Changed return type | Yes |
| Changed behavior | Usually |
| Added required parameter | Yes |
| Added optional parameter | No |
| Added new function | No |
| Bug fixes | No |

### Breaking Change Announcement

Minimum 4 weeks before release:

```markdown
## Breaking Change Warning: v2.0.0

**Coming:** 2026-04-25

### Changes

- `old_function()` will be removed
  - Use `new_function()` instead

- `OldStruct` will be renamed
  - Use `NewStruct` instead

### Migration Guide

[Link to migration guide]
```

## Version Compatibility Matrix

| Package | Min Rust | Min Node | Min Go | Min Python |
|---------|---------|----------|--------|------------|
| hexagonal-rs | 1.70 | N/A | N/A | N/A |
| hexagonal-ts | N/A | 18 | N/A | N/A |
| hexagonal-go | N/A | N/A | 1.21 | N/A |
| hexagonal-py | N/A | N/A | N/A | 3.10 |

## References

- [SemVer.org](https://semver.org)
- [Keep a Changelog](https://keepachangelog.com)
- [ADR-0002: Package Classification](./adrs/0002-package-classification-framework.md)

---

*Maintained by: Architecture Guild*
*Last Updated: 2026-03-25*
