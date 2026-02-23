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
