# Phenotype Repository Governance Policy

## Overview
This document establishes governance standards across the Phenotype organization repositories. It covers code ownership, PR processes, branch protection, and bot account handling.

---

## 1. Code Ownership (CODEOWNERS)

### Purpose
The CODEOWNERS file defines who is responsible for reviewing and maintaining code in specific parts of the repository.

### Format
```
# Repository root
* @KooshaPari

# Documentation
docs/ @KooshaPari
*.md @KooshaPari
```

### Key Responsibilities
- **Code Review**: Listed owners must review PRs touching their areas
- **Maintenance**: Owners ensure code quality and functionality
- **Escalation**: Owners handle disputes or blocking reviews

### Guidelines
- One primary owner per area (scalable to teams later)
- CODEOWNERS file is automatically enforced by GitHub
- Owners can delegate reviews but remain accountable

---

## 2. Pull Request Process

### Standard Workflow
1. **Create branch** from `main`
   - Use descriptive names: `feat/`, `fix/`, `docs/`, `chore/`
   - Example: `feat/user-authentication`, `fix/database-query`

2. **Open PR** with template:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type
   - [ ] Bug fix
   - [ ] Documentation  
   - [ ] New feature
   - [ ] Breaking change
   
   ## Testing
   How to verify this works
   ```

3. **Get approval** (minimum 1 code owner)

4. **Merge** using squash merge for clean history

### Branch Protection Rules
- **Require status checks** (build, test, lint)
- **Require PR review** (1 approval minimum)
- **Dismiss stale reviews** on new commits
- **Require branch to be up to date** before merging
- **Restrict who can push** to main

### Review Process
- Owners should review within 24 hours
- Use "Request changes" for blocking issues
- Use "Comment" for suggestions
- Approve once satisfied

---

## 3. Commit Standards

### Commit Message Format
Use conventional commits for clarity:
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (formatting, missing semicolons)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Test additions/updates
- `chore:` Build, dependencies, tooling

### Example
```
feat: add user authentication API

Add JWT-based authentication with token refresh.
Implements login/logout endpoints and middleware.

Closes #123
```

---

## 4. Bot Account Handling

### Supported Bot Accounts
- **jif-oai**: Internal automation bot
- **app/dependabot**: Dependency updates
- **claude-code**: Code generation bot

### Auto-Labeling
Bot PRs are automatically labeled with:
- `bot-authored`: Identifies PR source
- `needs-review`: Requires human review

### Review Policy
1. Bot PRs require same approval as human PRs
2. Review for correctness, not authorship
3. Can request changes or dismiss if needed
4. Dependabot updates are typically low-risk

### Examples
```yaml
# Dependabot PR
- Type: Dependency update
- Review: Check for breaking changes
- Decision: Merge if compatible

# jif-oai PR  
- Type: Automation output
- Review: Verify accuracy
- Decision: Merge if correct

# claude-code PR
- Type: Code generation
- Review: Review like human code
- Decision: Request changes if needed
```

---

## 5. Branch Naming Convention

### Allowed Prefixes
```
feat/          Feature development
fix/           Bug fixes
docs/          Documentation
style/         Code formatting
refactor/      Code refactoring
perf/          Performance
test/          Testing
chore/         Build, CI, tooling
hotfix/        Urgent fixes
```

### Examples
```
feat/user-authentication
fix/database-query-bug
docs/api-documentation
chore/update-dependencies
hotfix/security-patch
```

### Rules
- Use lowercase
- Separate words with hyphens
- Keep names descriptive but concise
- Maximum 50 characters recommended

---

## 6. Main Branch Protection

### What's Protected
The `main` branch is protected to ensure stability:
- ✅ All status checks pass
- ✅ At least 1 PR approval
- ✅ PR review required (not just approval)
- ✅ Fresh branch with latest main
- ✅ No direct pushes allowed

### Exceptions
- **Emergency hotfixes**: Use `hotfix/` prefix, still requires PR
- **Release updates**: Follow standard PR process

### Enforcement
- GitHub Actions checks all commits
- Automatic status check enforcement
- Admin override requires special justification

---

## 7. Release Management

### Release Process
1. Create `release/vX.Y.Z` branch
2. Update version numbers
3. Update CHANGELOG
4. Create PR for release notes
5. Get approval
6. Create GitHub Release with tag

### Version Numbering
Use Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: `v2.3.1`

---

## 8. Governance File Locations

### Required Files
- **CODEOWNERS**: Repository root
  - Defines code ownership
  - Automatically enforced by GitHub

- **CI/CD Workflow**: `.github/workflows/ci.yml`
  - Defines build, test, lint steps
  - Runs on PR and push to main

- **This File**: `GOVERNANCE.md` or `GOVERNANCE`
  - Repository-wide governance policy
  - Establishes review standards

---

## 9. Escalation Process

### If Review is Blocked
1. **Check CODEOWNERS** for responsible party
2. **@mention** the owner with question
3. **Wait 24 hours** for response
4. **Escalate** to @KooshaPari if needed

### If PR is Stale
- **Author responsibility**: Update PR status
- **Automatic cleanup**: Stale PRs marked after 30 days
- **Closure**: PRs can be closed without merge if no activity

---

## 10. Compliance Checklist

Before merging a PR, verify:
- [ ] PR title follows convention
- [ ] Description explains changes
- [ ] At least 1 code owner approved
- [ ] All status checks pass
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Commit message is clear
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if applicable)

---

## 11. Questions & Support

For governance questions:
- **Code ownership**: Check CODEOWNERS file
- **PR process**: Read this document
- **Tool issues**: Contact @KooshaPari
- **Policy changes**: Open discussion PR

---

## Appendix: GitHub CLI Commands

### Common Operations
```bash
# Create PR
gh pr create --title "Title" --body "Description"

# Add labels
gh pr edit 123 --add-label "needs-review"

# Request changes
gh pr review 123 --request-changes

# Approve PR
gh pr review 123 --approve

# Merge PR
gh pr merge 123 --squash

# List open PRs
gh pr list --state open

# Close PR
gh pr close 123
```

---

**Last Updated**: 2026-03-26  
**Maintained By**: @KooshaPari  
**Status**: Active
