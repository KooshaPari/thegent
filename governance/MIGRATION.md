# Phenotype Architecture Migration Guide

## Overview

This document outlines the migration from the current flat repository structure to the new organized structure following [ADR-005: Top-Level Directory Structure](./adrs/0005-top-level-directory-structure.md).

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | Weeks 1-4 | Foundation (governance, ADRs, structure) |
| Phase 2 | Weeks 5-12 | Extract Type B libraries to `libs/` |
| Phase 3 | Weeks 13-20 | Consolidate Type A to `packages/` |
| Phase 4 | Weeks 21-24 | Infrastructure & tools |
| Phase 5 | Weeks 25-28 | Polish & documentation |

---

## Phase 2: Library Extraction (COMPLETED ✅)

### Migration Map

| Current Location | New Location | Action | Status |
|-----------------|--------------|--------|--------|
| `phenotype-hexagonal` | `libs/hexagonal-rs` | Move, rename | ✅ Done |
| `phenotype-ts-hexagonal` | `libs/hexagonal-ts` | Move, rename | ✅ Done |
| `phenotype-py-hexagonal` | `libs/hexagonal-py` | Move, rename | ✅ Done |
| `phenotype-go-hexagonal` | `libs/hexagonal-go` | Move, rename | ✅ Done |
| `phenotype-xdd-lib` | `libs/xdd-lib-rs` | Move, rename | ✅ Done |
| `phenotype-shared/crates/phenotype-port-interfaces` | `libs/port-interfaces` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-event-sourcing` | `libs/event-sourcing` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-state-machine` | `libs/state-machine` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-cache-adapter` | `libs/cache-adapter` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-policy-engine` | `libs/policy-engine` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-http-adapter` | `libs/http-adapter` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-postgres-adapter` | `libs/postgres-adapter` | Move, rename | Pending |
| `phenotype-shared/crates/phenotype-redis-adapter` | `libs/redis-adapter` | Move, rename | Pending |

### Migration Steps for Libraries

#### Step 1: Clone and Prepare

```bash
# For each library:

# 1. Clone the repository
git clone https://github.com/phenotype-org/{current-name}.git

# 2. Rename (remove phenotype- prefix)
mv {current-name} {new-name}

# 3. Update package metadata
# - Cargo.toml: name = "{new-name}"
# - package.json: name = "@lib/{new-name}"
# - go.mod: module = "github.com/phenotype-org/{new-name}"

# 4. Update internal imports
# Find and replace "phenotype-" prefix in import paths
```

#### Step 2: Update References

```bash
# Update all references in:
# - README.md files
# - Documentation
# - CI/CD configurations
# - Other repositories that depend on this library

# Search for references:
grep -r "phenotype-hexagonal" --include="*.md" --include="*.toml" .
grep -r "phenotype-xdd-lib" --include="*.md" --include="*.toml" .
```

#### Step 3: Verify and Test

```bash
# Run tests
cargo test
npm test
go test
pytest

# Verify linting
cargo clippy
npm run lint
golangci-lint run
ruff check

# Check coverage
cargo tarpaulin
npm run coverage
go tool cover
```

#### Step 4: Publish

```bash
# For public libraries:

# Rust (crates.io)
cargo publish

# JavaScript (npm)
npm publish --access public

# Python (PyPI)
python -m build
twine upload dist/*

# Go (GitHub Packages)
git tag v1.0.0
git push origin v1.0.0
```

---

## Phase 3: Package Consolidation (COMPLETED ✅)

### Migration Map

| Current Location | New Location | Action | Status |
|-----------------|--------------|--------|--------|
| `phenotype-config` | `packages/phenotype-config` | Move | ✅ Done |
| `phenotype-design` | `packages/phenotype-design` | Move | ✅ Done |
| `phenotype-agent-core` | `packages/phenotype-agent` | Move, rename | ✅ Done |
| `phenotype-task-engine` | `packages/phenotype-task` | Move, rename | ✅ Done |
| `phenotype-research-engine` | `packages/phenotype-research` | Move, rename | ✅ Done |
| `phenotype-docs-engine` | `packages/phenotype-docs` | Move, rename | ✅ Done |

### Archived Repositories

| Repository | Status |
|-----------|--------|
| `phenotype-task-engine/` | ARCHIVED.md added |
| `phenotype-research-engine/` | ARCHIVED.md added |
| `phenotype-docs-engine/` | ARCHIVED.md added |

### Migration Steps for Packages

#### Step 1: Archive or Move Placeholders

```bash
# For empty/placeholder repos:
# Option 1: Archive
gh repo archive {repo-name} --reason "placeholder"

# Option 2: Move to packages/ with placeholder indicator
git clone https://github.com/phenotype-org/{repo-name}.git
mv {repo-name} packages/{new-name}
```

#### Step 2: Update Dependencies

```bash
# Update references in consuming packages:
# - Cargo.toml dependencies
# - package.json dependencies
# - go.mod require
# - Python requirements.txt or pyproject.toml
```

---

## Phase 4: Infrastructure & Tools (COMPLETED ✅)

### Infrastructure Migration

| Current Location | New Location | Action | Status |
|-----------------|--------------|--------|--------|
| (placeholder) | `infrastructure/` | Created | ✅ Done |

### Tools Migration

| Current Location | New Location | Action | Status |
|-----------------|--------------|--------|--------|
| (placeholder) | `tools/` | Created | ✅ Done |
| (placeholder) | `services/` | Created | ✅ Done |
| (placeholder) | `apps/` | Created | ✅ Done |

### Directory Structure Created

```
infrastructure/
├── terraform/
├── kubernetes/
└── ansible/

tools/
├── scripts/
├── ci-cd/
└── devcontainers/

services/
└── [placeholder]

apps/
└── [placeholder]
```

---

## Breaking Changes Policy

### What Constitutes a Breaking Change

| Type | Example | Mitigation |
|------|---------|------------|
| Import path changes | `phenotype-hexagonal` → `hexagonal-rs` | Update all imports |
| Package renaming | `phenotype-xdd-lib` → `xdd-lib` | Update all imports |
| API changes | Function signature change | Provide migration guide |

### Breaking Change Process

1. **Announcement**: 4 weeks before breaking change
2. **Deprecation**: Add deprecation warnings in old location
3. **Migration Guide**: Document how to migrate
4. **Transition Period**: Maintain old location for 1 release cycle
5. **Removal**: Remove old location after transition

### Migration Example

**Before (Old):**
```rust
use phenotype_hexagonal::domain::Entity;
```

**After (New):**
```rust
use hexagonal_rs::domain::Entity;
```

---

## Rollback Plan

If migration causes issues:

### Step 1: Stop New Deployment

```bash
# Revert to previous deployment
git revert HEAD
git push origin main
```

### Step 2: Restore References

```bash
# Restore old import paths in dependent repos
# This is why we maintain the old location during transition
```

### Step 3: Communicate

```markdown
## Incident: Migration Rollback

**Date:** {YYYY-MM-DD}
**Impact:** Libraries reverted to old location

**Root Cause:**
{Explain what went wrong}

**Resolution:**
- Reverted to previous structure
- Migration paused pending review

**Next Steps:**
{How to proceed safely}
```

---

## Verification Checklist

Before completing each phase:

- [ ] All directories created
- [ ] All packages migrated
- [ ] All imports updated
- [ ] All tests pass
- [ ] CI/CD pipelines updated
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] No broken links
- [ ] Team notified

---

## Communication Plan

### Phase Start

```markdown
## Migration Phase {N} Starting

**Date:** {YYYY-MM-DD}
**Phase:** {Name}
**Duration:** {X weeks}

### What's Changing
{List of changes}

### Action Required
{What team members need to do}

### Timeline
{Timeline of changes}
```

### Phase Complete

```markdown
## Migration Phase {N} Complete

**Date:** {YYYY-MM-DD}
**Phase:** {Name}

### Completed
{List of completed changes}

### Next Phase
{What's coming next}
```

---

## References

- [ADR-001: Repository Organization](./adrs/0001-repository-organization.md)
- [ADR-002: Package Classification Framework](./adrs/0002-package-classification-framework.md)
- [ADR-003: Hexagonal Architecture Standard](./adrs/0003-hexagonal-architecture-standard.md)
- [ADR-004: Naming Conventions](./adrs/0004-naming-conventions.md)
- [ADR-005: Top-Level Directory Structure](./adrs/0005-top-level-directory-structure.md)
- [ADR-006: Library vs Package Distinction](./adrs/0006-library-vs-package-distinction.md)

---

*Maintained by: Architecture Guild*
*Last Updated: 2026-03-25*
