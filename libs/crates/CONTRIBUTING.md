# Contributing to Phenotype — Crates

Thank you for your interest in contributing! This document outlines the process for contributing to the `crates` repository.

## Development Workflow

- **Create a feature branch** from `main` using: `git checkout -b fix/description`
- **Code standards**: Format with `cargo fmt` and lint with `cargo clippy -- -D warnings`
- **Testing**: Add tests for all new code; run `cargo test` before pushing
- **Follow the branch-based delivery protocol** in CLAUDE.md
- **Ensure all CI policy gates are green** before requesting review (build, test, clippy, fmt, security)
- **Document all user-facing changes** in CHANGELOG.md with the format:
  - Type: `feat:`, `fix:`, `docs:`, etc.
  - Description: Brief, clear summary
  - Example: `feat: add incremental export support`

## Code Quality

Before committing:

```bash
cargo fmt                    # Format code
cargo clippy --all-targets   # Lint (fix warnings)
cargo test --lib             # Test (must pass)
./scripts/quality-gate.sh verify  # Full check
```

## Testing Requirements

- **All new code must include tests**
- Tests must run: `cargo test --lib`
- Aim for >80% code coverage
- Test format: descriptive names like `test_<function>_<scenario>`

## Documentation

- Update README.md for user-facing features
- Update CHANGELOG.md for all changes
- Add doc comments (`///`) to public APIs
- Include examples in complex function docs

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add feature description
fix: fix bug description
docs: update documentation
test: add test coverage
refactor: improve code structure
```

## PR Checklist

- [ ] All tests pass: `cargo test`
- [ ] No clippy warnings: `cargo clippy -- -D warnings`
- [ ] Code formatted: `cargo fmt --check`
- [ ] Documentation updated (README, CHANGELOG, doc comments)
- [ ] Commit messages follow Conventional Commits
- [ ] No breaking changes without justification
- [ ] Governance policy validation passes: `./scripts/policy-gate.sh`
