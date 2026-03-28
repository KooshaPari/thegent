# Phenotype Engineering Governance

**Version:** 1.0.0
**Date:** 2026-03-25
**Status:** Active

---

## Overview

This document establishes governance rules for the Phenotype polyrepo ecosystem, including:
- Branch naming conventions
- PR requirements and merge rules
- Release processes
- Rollback procedures
- Code quality standards

---

## Repository Organization

### Naming Conventions

See **`docs/engineering/PACKAGE_REPO_NAMING_TAXONOMY.md`** for full tiers (org-bound `phenotype-*` vs neutral productized libs).

| Type | Pattern | Example |
|------|---------|---------|
| **Phenotype org-bound** | `phenotype-{domain}` (use sparingly) | `phenotype-config`, `phenotype-design` |
| **Productized / marketable lib** | Neutral descriptive name | `portkey`, `dual-write`, `mesh-bus` |
| **Named product / app** | Product brand (not `phenotype-`) | `helios-cli`, `thegent`, `portage` |
| **Templates** | `template-*`, `scaffold-*` | `template-lang-go` |
| **Agent / infra components** | `{component}` or product name | `agent-cache`, `infrakit` |

### Directory Structure (All Repos)

```
repo/
├── cmd/                    # Entry points
├── internal/               # Private code
│   ├── domain/           # Core business logic
│   ├── application/      # Use cases + ports
│   └── infrastructure/   # Adapters
├── pkg/                   # Public packages
├── api/                   # API definitions
├── configs/               # Configuration
├── scripts/               # Scripts
├── docs/                  # Documentation
├── tests/                 # Integration tests
├── Makefile
└── README.md
```

---

## Branch Naming

### Format

```
{type}/{scope}/{description}
```

### Types

| Type | Description |
|------|-------------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `refactor/` | Code refactoring |
| `docs/` | Documentation |
| `test/` | Tests |
| `chore/` | Maintenance |
| `arch/` | Architecture changes |
| `hotfix/` | Production emergency fix |

### Examples

```
feat/domain/add-order-aggregate
fix/cli/resolve-target-not-found
refactor/adapter/sqlite-optimization
arch/hexagonal/migrate-to-ports
hotfix/security/cve-2024-1234
```

---

## Pull Request Rules

### Requirements

| Requirement | Description | Required |
|------------|-------------|----------|
| **Title** | Conventional commit format | ✅ |
| **Description** | Summary, changes, testing | ✅ |
| **Tests** | Unit + integration tests | ✅ |
| **Linting** | All linters passing | ✅ |
| **CI** | All CI checks green | ✅ |
| **Size** | < 1000 lines changed | ✅ (soft) |
| **Review** | At least 1 approval | ✅ |

### PR Title Format

```
{type}({scope}): {description}

Examples:
feat(domain): add Order aggregate with validation
fix(cli): resolve target not found error
refactor(adapter): optimize SQLite queries
```

### PR Description Template

```markdown
## Summary
Brief description of the change.

## Changes
- List of specific changes made
- Include file names if relevant

## Testing
- How was this tested?
- Include test results

## Related Issues
- Closes #{issue}
- Related to #{issue}
```

### Merge Rules

| Rule | Description |
|------|-------------|
| **Linear History** | Squash and merge preferred |
| **CI Required** | All checks must pass |
| **Reviews** | At least 1 approval |
| **Blocking** | No merge with failing checks |

### Auto-Merge Settings

```yaml
# .github/merge-rules.yaml
require_checks: true
blocking_checks: [lint, test, build]
merge_method: squash
delete_branch: true
auto_delete_head_branch: true
```

---

## Roll Rules

### Branch Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   feature   │───▶│   review    │───▶│   merged    │
│   branch    │    │   branch    │    │   branch    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                    │
       │         ┌─────────────┐            │
       └────────▶│   draft     │───────────┘
                 │   PR        │
                 └─────────────┘
```

### Worktree Policy

Per project guidelines:
- Canonical state stays on `main`
- All work in worktrees under `repos/worktrees/{project}/`
- Example: `worktrees/heliosApp/fix/ci-workflow-fix`

### Finalization Order

```bash
# Run governance script for safe cleanup
./scripts/worktree_governance.sh oldest-first
```

---

## Release Process

### Version Bumping

| Type | Bump | Example |
|------|------|---------|
| **Patch** | PATCH | `1.0.0` → `1.0.1` |
| **Minor** | MINOR | `1.0.0` → `1.1.0` |
| **Major** | MAJOR | `1.0.0` → `2.0.0` |

### Release Checklist

- [ ] Update `CHANGELOG.md`
- [ ] Bump version in manifest
- [ ] Create annotated tag `v{version}`
- [ ] Run all tests
- [ ] Build artifacts
- [ ] Publish to registry
- [ ] Create GitHub release
- [ ] Announce in Slack

### Git Tag Format

```bash
# Annotated tag with message
git tag -a v1.2.3 -m "Release v1.2.3: Add new feature"

# Push tag
git push origin v1.2.3
```

---

## Rollback Procedures

### Hotfix Process

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/security-fix

# 2. Make minimal fix
# ... fix code ...

# 3. Test thoroughly
cargo test
cargo clippy

# 4. Create PR with "hotfix/" prefix
gh pr create --title "hotfix: critical security fix" --base main

# 5. Fast-track review
# 6. Merge immediately
gh pr merge --squash --delete-branch
```

### Revert Process

```bash
# Revert a merged PR
gh pr revert {pr-number}

# Or manually
git revert {commit-sha}
git push origin main
```

### Database Migration Rollback

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade {revision}
```

---

## Code Quality Standards

### Linting

| Language | Linter | Config |
|----------|--------|--------|
| Rust | `clippy` + `rustfmt` | `.clippy.toml` |
| Python | `ruff` + `mypy` | `pyproject.toml` |
| Go | `golangci-lint` | `.golangci.yml` |
| TypeScript | `eslint` + `prettier` | `.eslintrc` |

### Testing Requirements

| Level | Coverage Target | Tool |
|-------|----------------|------|
| Unit | > 80% | `cargo test`, `pytest` |
| Integration | All adapters | `cargo test`, `pytest` |
| Contract | API compatibility | `pact`, `schemathesis` |

### Documentation

| Type | Required | Location |
|------|----------|----------|
| README | ✅ | Root |
| COMPARISON.md | ✅ (forks) | Root or docs/ |
| Architecture | ✅ (complex) | docs/ARCHITECTURE.md |
| API Docs | ✅ (services) | api/ or docs/ |
| CHANGELOG | ✅ (published) | CHANGELOG.md |

---

## Anti-Patterns (Prohibited)

### Code

| Anti-Pattern | Description | Detection |
|--------------|-------------|-----------|
| `unwrap()` | Panic on error | Clippy E1103 |
| `print()` | Debug statement | Lint rule |
| Magic numbers | Unnamed constants | Lint rule |
| Dead code | Unused functions | Lint rule |

### Git

| Anti-Pattern | Description | Prevention |
|--------------|-------------|-------------|
| Force push | Overwrite history | Branch protection |
| Direct main push | Bypass review | Branch protection |
| Large PRs | > 1000 lines | PR template warning |

---

## Compliance Checklist

For each PR, verify:

- [ ] **SOLID** - Single responsibility, proper abstractions
- [ ] **DRY** - No obvious code duplication
- [ ] **KISS** - Simple solution preferred
- [ ] **YAGNI** - No speculative code
- [ ] **Hexagonal** - Domain isolated from infrastructure
- [ ] **Tests** - Domain logic has unit tests
- [ ] **Linting** - All linters pass
- [ ] **Docs** - Public API documented

---

## See Also

- [PHENOTYPE_WBS_300.md](../PHENOTYPE_WBS_300.md) - Work breakdown structure
- [ADR-001-REPOSITORY-ORGANIZATION.md](../ADR-001-REPOSITORY-ORGANIZATION.md) - Architecture decisions
- [.forge/skills/xdd-methodologies/SKILL.md](../.forge/skills/xdd-methodologies/SKILL.md) - x-DD patterns
- [plans/2026-03-25-polyrepo-restructuring.md](../plans/2026-03-25-polyrepo-restructuring.md) - Restructuring plan
