# Contributing to Phenotype

Thank you for your interest in contributing to Phenotype! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct.

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:
1. Check existing issues
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Code samples

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Describe the problem you're solving
4. Provide use cases
5. Consider backward compatibility

### Pull Requests

## Development Process

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/phenotype.git
cd phenotype/repos
```

### 2. Create a Branch

```bash
git checkout -b type/description

# Examples:
git checkout -b feature/task-scheduler
git checkout -b fix/memory-leak
git checkout -b docs/api-reference
```

### 3. Make Changes

- Follow coding standards
- Write tests
- Update documentation
- Commit using conventional commits

### 4. Test Your Changes

```bash
# Run all tests
bun test && pytest && cargo test

# Run linting
bun run lint && ruff check . && cargo clippy
```

### 5. Push and Create PR

```bash
git push origin type/description
```

Then open a pull request on GitHub.

## Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

### Examples

```
feat(agent): add task priority scheduling

Implemented priority-based task scheduling algorithm.
Fixes #123

Closes #456
```

```
fix(core): resolve race condition in event handler

The event handler was not thread-safe, causing
inconsistent state under high load.
```

## Coding Standards

See [governance/standards/](../governance/standards/) for language-specific standards:

- [Rust](../governance/standards/rust.md)
- [TypeScript](../governance/standards/typescript.md)
- [Python](../governance/standards/python.md)
- [Go](../governance/standards/go.md)

## Pull Request Process

### Before Submitting

- [ ] Code follows standards
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commits are atomic
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Summary

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe testing performed

## Checklist

- [ ] Code follows standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. Automated checks must pass
2. At least one maintainer review
3. Address feedback
4. Squash and merge

## Code Review Guidelines

### For Authors

- Respond to all comments
- Be receptive to feedback
- Explain your decisions
- Update PR based on feedback

### For Reviewers

- Be constructive and respectful
- Explain the "why" behind suggestions
- Reference existing code/standards
- Approve when satisfied

## Style Guides

### Git

- Use conventional commits
- Write meaningful commit messages
- Keep commits atomic
- Rebase vs merge

### Documentation

- Use clear, concise language
- Include code examples
- Keep docs up to date
- Follow existing patterns

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- Release notes
- Contributor list

## Questions?

- Open an issue
- Join our Discord
- Email maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
