# Pull Request Standards

## PR Workflow

All changes to main MUST go through pull requests:

1. Create a feature branch: `git checkout -b feat/description`
2. Make commits following [commit-conventions.md](commit-conventions.md)
3. Push and create PR: `gh pr create`
4. Address review feedback
5. Ensure all checks pass
6. Merge via `gh pr merge`

## PR Title & Description

### Title Format

```
<type>(<scope>): <description>
```

- Match commit type and scope (see [commit-conventions.md](commit-conventions.md))
- Keep under 72 characters
- Use imperative mood

Examples:

```
feat(auth): implement JWT token refresh
fix(api): handle missing Content-Type header
docs(guides): add Docker setup instructions
chore(deps): upgrade ruff to 0.1.0
```

### Description Template

```markdown
## Summary

[One-sentence summary of what this PR does]

## Motivation & Context

- Why is this change needed?
- What problem does it solve?
- Reference related issues: Fixes #123, Related to #456

## Changes Made

- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## Files Changed

- `src/module/file.py` — Brief description
- `tests/test_file.py` — Brief description

## Testing

Describe how this change was tested:

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Edge cases tested
- [ ] Coverage maintained/improved

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] All tests passing
- [ ] No new warnings/linter issues

## Screenshots / Evidence

[If applicable, include screenshots, logs, or benchmark results]

## Related

- Fixes #123
- Related to #456
- Depends on #789
```

## PR Size & Scope

### Ideal PR Size

- **Small**: 100-300 lines of changes, 1-3 files
- **Medium**: 300-600 lines of changes, 3-8 files
- **Large**: 600+ lines (should be split into multiple PRs)

### Scope Rules

- **One concern per PR**: One feature, one fix, one refactor
- **Stacked PRs**: For multi-part changes, create separate PRs with explicit dependencies
- **No refactoring + features**: Don't mix refactoring with new features
- **No style + substance**: Don't mix style changes with logic changes

## Branch Protection Rules

All PRs to main MUST satisfy:

1. **At least one approval** (if review is required)
2. **All CI checks passing**:
   - Build succeeds
   - Lints pass
   - Tests pass (unit + integration)
   - Coverage maintained
   - Security scans clean
   - Type checking passes
3. **All conversations resolved** (no pending review comments)
4. **Up-to-date with main** (rebased or merged)
5. **No force pushes** (except to own feature branches)

## Code Review Expectations

### For Authors

- **Request review early**: Don't wait until PR is "done"
- **Respond promptly**: Address feedback quickly
- **Engage in discussion**: Ask for clarification if feedback is unclear
- **Don't dismiss feedback**: Even if you disagree, discuss it
- **Test locally**: Verify all tests pass before requesting review

### For Reviewers

- **Review within 24 hours** when possible
- **Be constructive**: Suggest improvements, don't just criticize
- **Ask questions**: "Why did you choose this approach?" helps authors think through decisions
- **Test locally**: Run the code, test edge cases
- **Approve once satisfied**: Don't demand perfection, aim for "good enough"

## Merge Strategy

### Standard Merge (Recommended)

Preserves full commit history and branching topology:

```bash
gh pr merge --merge
# or git merge --no-ff <branch>
```

### Squash Merge

For small PRs with many work-in-progress commits:

```bash
gh pr merge --squash
```

**When to use**:
- WIP commits that don't add value individually
- Small fixes or docs updates
- Feature branches with many "fix typo" commits

### Rebase Merge

For linear history (rare):

```bash
gh pr merge --rebase
```

**When to use**:
- Never on main; only on feature branches
- Use locally to clean up before standard merge

### DO NOT USE

- Force push to main: `git push -f origin main` ❌
- Delete and recreate: `git reset --hard` on main ❌
- Force merge: `git merge -f` ❌

## Handling CI Failures

### If CI Fails

1. **Identify the failure**: Read CI logs carefully
2. **Reproduce locally**: Run the same tests/checks locally
3. **Fix the issue**: Don't dismiss as "pre-existing" or "unrelated"
4. **Push fix**: Commit and push the fix
5. **Re-run CI**: Verify all checks pass

### If Failure is Pre-Existing

- **Still required to fix**: Inherit failures from main? Fix them in your PR.
- **Document in PR**: Explain why the failure existed and what you did to fix it.
- **Never merge failing**: Don't merge PRs with any red checks.

### If Failure is External

- **Infrastructure issues**: GitHub Actions billing, rate limits, etc.
- **Documented exception**: GitHub Actions billing failures only
- **For everything else**: Fix or document in PR

## PR Lifecycle

### Stages

1. **Draft**: Use `gh pr create --draft` to flag as WIP
2. **Review**: Request reviewers, mark as ready
3. **Approved**: All feedback addressed, reviews approved
4. **Checks Passing**: All CI/CD checks green
5. **Merged**: Squash/merge/rebase as appropriate

### Auto-Closing Stale PRs

- PRs inactive for 30+ days should be closed or updated
- If blocked: document blocker in PR comments

## Examples

### Good PR

```markdown
## Summary
Implement JWT token refresh to prevent session timeouts during long user sessions.

## Motivation & Context
Users with active sessions over 1 hour were being logged out. JWT tokens expire after 1h, and there was no refresh mechanism.

Fixes #42

## Changes Made
- Add `/auth/refresh` endpoint to exchange expired token for new one
- Store refresh token in secure HTTPOnly cookie
- Add automatic refresh on 401 Unauthorized responses
- Add tests for normal flow and edge cases

## Testing
- [ ] Unit tests for refresh logic (PASS)
- [ ] Integration test for auth flow (PASS)
- [ ] Manual testing with 1.5h session (PASS)
- [ ] Coverage: 92% (↑2%)

## Checklist
- [x] Code follows style guidelines
- [x] Tests added and passing
- [x] Documentation updated
- [x] No breaking changes
```

### Problematic PR

```markdown
## Summary
Fixed some auth stuff and also refactored the API and updated dependencies

## Changes Made
- Refactored auth module (major changes)
- Updated 15+ dependencies
- Added new token refresh feature
- Changed API response format
- Fixed some tests

## Testing
Not sure, but it works locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [x] No breaking changes (changed multiple APIs but not marking as breaking)
```

## Stacked PRs

For large features requiring multiple PRs:

1. **First PR**: Base feature, from main → feature-branch-1
2. **Second PR**: Depends on first, from feature-branch-1 → feature-branch-2
3. **Third PR**: Depends on second, from feature-branch-2 → feature-branch-3

Link in description:

```markdown
## Stacked PR

This PR depends on #100.
See #101 for follow-up.

## Merge Order

1. Merge #99 first
2. Then merge this PR (#100)
3. Then merge #101
```

Merge in order: don't merge #100 until #99 is merged.

## Documentation

- **Update README**: If user-facing
- **Update CHANGELOG**: If releasing
- **Update API docs**: If API changes
- **Add examples**: Complex features should have examples

## When to Bypass Review

- **Personal WIP branches**: Can merge directly to own branch
- **Docs-only**: Minor documentation fixes can merge faster
- **CI infrastructure**: CI/CD config changes (with caution)

**Never bypass**:
- Core business logic
- Security-related code
- User-facing features
- API changes
