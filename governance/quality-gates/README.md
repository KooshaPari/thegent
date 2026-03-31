# Quality Gates

This directory contains quality gate configurations and documentation for the thegent project.

## Available Quality Gates

### Pre-Commit Hooks

Validate code before commits are made:

- **Lint checking**: Ruff, ESLint, golangci-lint, clippy
- **Type checking**: mypy, pyright, tsc
- **Format validation**: Black, Prettier, rustfmt, gofmt
- **Secret detection**: trufflehog (not gitleaks)
- **Trailing whitespace**: Catch common issues

### CI/CD Gates (GitHub Actions)

Run on every PR:

- **Build**: Compile/validate source code
- **Lint**: Full lint suite (0 errors policy)
- **Type**: Full type checking (0 errors policy)
- **Tests**: Unit, integration, E2E tests
- **Coverage**: Verify coverage thresholds met
- **Security**: SAST scanning (Semgrep, bandit)
- **Dependency audit**: Check for vulnerable deps

### Pre-Merge Checks

Required before merging to main:

- [x] All CI checks passing
- [x] Code review approved
- [x] Test coverage maintained/improved
- [x] No new linting issues
- [x] Commit messages follow convention
- [x] All conversations resolved

### Quality Gate Rules

#### Lint (0 Errors Policy)

**Rule**: No linting errors allowed in pull requests.

**When violation occurs**:
1. Fix the issue in your code
2. Commit the fix: `chore: resolve lint issue XYZ`
3. Push and re-run CI

**Suppressions**: Require inline justification
```python
# noqa: E501 -- line is a long URL (https://example.com/very/long/url)
long_url = "..."
```

Unacceptable reasons:
- "non-blocking" ❌
- "pre-existing" ❌
- "will-fix-later" ❌
- "not-our-code" ❌

#### Type Checking (0 Errors Policy)

**Rule**: Type checker must pass with 0 errors.

**When violation occurs**:
1. Add explicit type annotations
2. Or use `# type: ignore` with justification
3. Commit and push: `chore: resolve type issue`

**Example**:
```python
from typing import Any

# type: ignore -- external library lacks type hints
import untyped_library
```

#### Test Coverage (Minimum Thresholds)

**Rule**: Coverage must meet or exceed minimums.

**Minimums**:
- Lines: 80%
- Branches: 75%
- Functions: 80%

**When coverage drops**:
1. Add tests for uncovered code
2. Re-run coverage: `pytest --cov`
3. Commit new tests
4. Push and verify CI passes

**Exceptions**:
- Generated code (auto-formatted, minified)
- Third-party integrations (vendor code)
- Thin wrappers with obvious behavior

#### Commit Messages

**Rule**: Follow commit convention format.

**Format**: `<type>(<scope>): <subject>`

**Validation**:
- Automatic pre-commit hook
- Manual check by reviewers
- CI validation (optional)

See [../standards/commit-conventions.md](../standards/commit-conventions.md)

#### Security Scanning

**Rule**: Zero high/critical vulnerabilities.

**Scans**:
1. SAST: Semgrep, bandit (Python), gosec (Go)
2. Dependency audit: pip-audit, npm audit, cargo-audit
3. Secret detection: trufflehog
4. Infrastructure: hadolint, tfsec

**When vulnerabilities found**:
1. Classify by severity (P1/P2/P3)
2. Fix or mitigate immediately
3. Document non-fixable issues
4. Update security policy if needed

#### FR Test Traceability

**Rule**: All tests must reference an FR ID.

**Traceability methods**:
1. Pytest marker: `@pytest.mark.requirement("FR-THEGENT-001")`
2. Comment tag: `# @trace FR-THEGENT-001`
3. Docstring: `Traces to: FR-THEGENT-001`
4. Test name: `test_FR_THEGENT_001_...`

**Verification**:
```bash
# Find all tests with FR references
grep -r "FR-THEGENT" tests/

# Find orphaned tests (no FR reference)
grep -r "^def test_" tests/ | grep -v FR-THEGENT | grep -v "test_helper\|test_fixture"
```

## Setup

### Pre-Commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Or if using uv:

```bash
uv pip install pre-commit
pre-commit install
```

### Running Quality Checks Locally

```bash
# Run all quality checks
task quality

# Run specific checks
task lint
task type-check
task test
task coverage

# Run pre-commit on staged files
pre-commit run --all-files
```

### GitHub Actions Configuration

Quality gates run automatically on:
- **Every PR push**: Run lint, type, test, coverage, security
- **Before merge**: All checks must pass
- **Daily scheduled**: Run full security audit, dependency check

## Common Issues & Solutions

### Lint Failure

**Problem**: Linter reports errors on PR

**Solution**:
```bash
# Fix automatically (if supported)
ruff check . --fix

# Or fix manually
# Then commit the fix
git add .
git commit -m "chore: resolve lint issues"
git push
```

### Type Checking Failure

**Problem**: Type checker reports errors

**Solution**:
```bash
# Add explicit type hint
def get_user(user_id: int) -> Optional[User]:
    ...

# Or suppress with comment (if necessary)
result: Any = external_api_call()  # type: ignore -- no type hints available
```

### Coverage Drop

**Problem**: Code coverage decreased in PR

**Solution**:
```bash
# Add tests for uncovered code
pytest --cov=src tests/ --cov-report=html
open htmlcov/index.html  # View coverage report

# Add tests
git add tests/
git commit -m "test: improve coverage for module X"
git push
```

### Test Failure

**Problem**: Test fails on CI but passes locally

**Solution**:
1. Run tests locally: `pytest tests/`
2. Check for environment differences (DB, cache, etc.)
3. Run with same Python version as CI
4. Check test isolation (no dependencies between tests)
5. Fix and re-run

### Security Vulnerability

**Problem**: Security scan finds vulnerability

**Solution**:
1. **If patchable**: Update dependency
   ```bash
   pip install --upgrade vulnerable-package
   ```
2. **If not patchable**: Document exception
   ```python
   # noinspection: security:XXX -- reason
   dangerous_function()
   ```
3. **Verify**: Re-run security scan

## Monitoring & Reporting

### Quality Dashboard (If Available)

- Coverage trends
- Lint/type issues over time
- Test pass rates
- Security scan results

### Manual Verification

```bash
# Coverage report
pytest --cov=src --cov-report=term-missing

# Lint report
ruff check src/

# Type report
mypy src/

# Test summary
pytest tests/ -v --tb=short
```

## Policies

### No Bypass

Quality gates cannot be bypassed without explicit approval:
- ❌ Merge with failing checks
- ❌ Force push to main
- ❌ Disable branch protection

### Exception Process

For rare exceptions (security incident, production emergency):

1. **Document reason**: Why bypass is necessary
2. **Get approval**: From tech lead/security lead
3. **Create follow-up**: Link to issue to resolve
4. **Add to log**: Document the exception

Example:
```
## Security Exception

**Reason**: Production incident XYZ requires urgent patch
**Approved by**: Security Lead (Jane Doe)
**Follow-up**: Issue #123 — full refactor in next release
**Documented**: Yes — see SECURITY.md
```

## Related Documents

- [../standards/code-style.md](../standards/code-style.md) — Code style standards
- [../standards/testing-standards.md](../standards/testing-standards.md) — Testing requirements
- [../standards/commit-conventions.md](../standards/commit-conventions.md) — Commit format
- [../standards/pr-standards.md](../standards/pr-standards.md) — PR requirements

---

**Last Updated**: 2026-03-29
**Owner**: Platform team
**Version**: 1.0
