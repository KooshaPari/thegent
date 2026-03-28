# Code Review Process

## Overview

This document defines the code review process for the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| TDD | Tests should be reviewed alongside code |
| BDD | User-facing features should have BDD tests |
| ATDD | Acceptance criteria should guide review |

## Review Checklist

### For Author

- [ ] Self-review code before requesting review
- [ ] Keep PRs small (<400 lines)
- [ ] Write clear PR description
- [ ] Include links to relevant ADRs
- [ ] Add screenshots for UI changes
- [ ] Ensure CI passes before requesting review
- [ ] Respond to feedback within 24 hours

### For Reviewer

- [ ] Review within 24 hours
- [ ] Understand the context and motivation
- [ ] Check for design consistency with ADR-003
- [ ] Verify naming follows ADR-004
- [ ] Check test coverage (see thresholds)
- [ ] Look for security issues
- [ ] Provide constructive, specific feedback

## Review Focus Areas

### 1. Correctness

- Does the code do what it's supposed to do?
- Are edge cases handled?
- Are errors handled properly?
- Are there potential bugs?

### 2. Design

- Does it follow hexagonal architecture?
- Are dependencies pointing in the right direction?
- Is the domain layer free of external dependencies?
- Are ports and adapters properly separated?

### 3. Testing

- Are there tests?
- Do tests cover the happy path?
- Are edge cases tested?
- Are error paths tested?
- Is coverage above threshold?

### 4. Security

- Is sensitive data handled properly?
- Are inputs validated?
- Are SQL/command injections prevented?
- Are secrets not committed?

### 5. Performance

- Are there obvious performance issues?
- Are queries optimized?
- Are expensive operations cached?
- Are N+1 queries avoided?

## Commenting Guidelines

### Prefix System

| Prefix | Meaning |
|--------|---------|
| `nit:` | Minor style issue, non-blocking |
| `suggestion:` | Optional improvement |
| `question:` | Seeking clarification |
| `issue:` | Must be addressed before merge |
| `blocker:` | Critical issue, must not merge |

### Example Comments

```
nit: Could use a more descriptive variable name here.

suggestion: Consider using a cache here to avoid repeated DB calls.

question: Why is this throwing away the error?

issue: This will panic if `user` is None. Need to handle this case.

blocker: This is a SQL injection vulnerability. Never concatenate user input into SQL.
```

## Merge Criteria

A PR can be merged when:

- [ ] All CI checks pass
- [ ] At least 1 approval from a code owner
- [ ] All `issue:` and `blocker:` comments resolved
- [ ] No unresolved conversations
- [ ] Test coverage meets threshold
- [ ] Documentation updated if needed
- [ ] CHANGELOG updated if needed

## Special Cases

### Hotfixes

- May be merged with 1 approval
- Must have clear description of the fix
- Must include test for the bug
- Must be tagged appropriately

### Large Refactors

- Requires 2+ approvals
- Should be broken into smaller PRs if possible
- Should have updated ADRs if architectural changes

### Dependency Updates

- Should be reviewed by security-conscious reviewer
- Should verify changelog for breaking changes
- Should run full test suite

---

*Maintained by: Architecture Guild*
