# Release Process

## Overview

This document defines the release process for the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| Semantic Versioning | Version scheme |
| CI/CD | Automated builds and tests |
| Trunk-Based Development | Frequent small releases |

## Version Scheme

### Libraries (Type B)

Follow [Semantic Versioning 2.0.0](https://semver.org/):

| Version | Type | Example |
|---------|------|---------|
| `MAJOR.MINOR.PATCH` | Full semver | `1.2.3` |
| `MAJOR.MINOR.PATCH-alpha.N` | Pre-release | `1.2.3-alpha.1` |
| `MAJOR.MINOR.PATCH-beta.N` | Beta | `1.2.3-beta.1` |

### Packages (Type A)

Internal versioning, options:

| Version | Type | Example |
|---------|------|---------|
| `0.1.0` | Initial | Pre-1.0 for internal |
| `date-based` | Snapshot | `2026.03.25.0` |

## Release Types

### Patch Release

**When:** Bug fixes, documentation updates, non-breaking changes

**Changes:**
- `PATCH` version increases
- No new features
- Backward compatible

**Process:**
1. Create PR with fix
2. Merge to main
3. CI creates release tag
4. Version bumped automatically

### Minor Release

**When:** New features, backward compatible

**Changes:**
- `MINOR` version increases
- `PATCH` resets to 0
- Backward compatible
- May include deprecations

**Process:**
1. Feature development in feature branches
2. Merge to main
3. Release PR with changelog update
4. CI creates release tag
5. Version bumped automatically

### Major Release

**When:** Breaking changes

**Changes:**
- `MAJOR` version increases
- `MINOR` and `PATCH` reset to 0
- Breaking changes documented
- Migration guide provided

**Process:**
1. Create release branch
2. Update for breaking changes
3. Create migration guide
4. Deprecation warnings in previous version
5. Announce to stakeholders

## Automated Releases

### GitHub Actions Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        uses: ./scripts/setup.sh

      - name: Test
        run: ./scripts/test.sh

      - name: Build
        run: ./scripts/build.sh

      - name: Publish
        uses: ./scripts/publish.sh
        env:
          # Credentials
```

### Release Tag Format

```
v{MAJOR}.{MINOR}.{PATCH}
```

Example: `v1.2.3`

## Changelog

### Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- New feature descriptions

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Vulnerability fixes

## [{VERSION}] - {DATE}

[... previous versions ...]
```

## Pre-release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Migration guide (if needed)
- [ ] Stakeholders notified (for major)
- [ ] Version tagged

## Post-release Checklist

- [ ] Release created on GitHub
- [ ] Package published (libraries)
- [ ] Announcement sent
- [ ] Old versions marked as unsupported (if applicable)

---

*Maintained by: Architecture Guild*
