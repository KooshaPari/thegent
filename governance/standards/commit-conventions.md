# Commit Conventions

## Format

All commits MUST follow this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

Must be one of:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (formatting, missing semicolons, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process, dependencies, or auxiliary tools
- **ci**: Changes to CI/CD configuration or scripts
- **security**: Security fixes or security-related changes

### Scope

The scope is optional but recommended. It should specify what part of the codebase is affected:

- `auth` — Authentication/authorization changes
- `api` — API routes or handlers
- `config` — Configuration management
- `db` — Database operations
- `cache` — Caching layer
- `cli` — CLI functionality
- `docs` — Documentation
- `tests` — Test infrastructure

Examples:

```
feat(auth): add token refresh mechanism
fix(api): handle null responses in user endpoint
docs(readme): update installation instructions
chore(deps): upgrade ruff to 0.1.0
```

### Subject

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize the first letter
- No period at the end
- Limit to 50 characters
- Be specific and descriptive

### Body

- Wrap at 72 characters
- Explain WHAT and WHY, not HOW
- Reference any related issues or tickets
- Separate from subject with a blank line

Example:

```
The login endpoint was timing out due to inefficient database queries.
This commit optimizes the query using proper indexes and adds
connection pooling.

Fixes #123
Related to #456
```

### Footer

Include:
- **Breaking changes**: Prefix with `BREAKING CHANGE:`
- **Issue references**: `Fixes #123`, `Closes #456`, `Related to #789`
- **Co-authors**: `Co-Authored-By: Name <email>`

Example:

```
BREAKING CHANGE: The /v1/users endpoint now requires authentication

Fixes #123
Related to #456
Co-Authored-By: John Doe <john@example.com>
```

## Examples

### Good Commits

```
feat(auth): implement JWT token refresh

Add automatic token refresh mechanism to prevent session timeouts.
Refresh tokens are stored in secure HTTPOnly cookies and validated
against a rotating key schedule.

Fixes #42
```

```
fix(api): handle missing Content-Type header in JSON routes

The JSON parser now defaults to UTF-8 encoding when Content-Type
is missing, preventing 400 errors on valid JSON payloads.

Related to #89
```

```
docs(getting-started): add Docker setup instructions

Include step-by-step Docker Compose setup for local development.
Covers all required services and environment configuration.
```

### Bad Commits

```
fixed stuff
```

```
Update code
```

```
MASSIVE REFACTOR - completely rewrote authentication system and
also added new caching layer and also fixed some bugs I found
```

## Commits as Documentation

- Each commit should be self-contained and logically complete
- Future developers should understand WHAT changed and WHY by reading the commit message
- Use commit messages to tell the story of how the code evolved

## Signing Commits (Recommended)

Consider signing commits with GPG:

```bash
git config user.signingkey <KEY_ID>
git config commit.gpgsign true
```

Then commit with `-S`:

```bash
git commit -S -m "feat: add signing to commits"
```

## Rewriting History

- **Never** rewrite public/shared branch history
- On feature branches, use interactive rebase to clean up commits before PR
- Use `git rebase -i` to squash, reorder, or reword commits
- After rebase, force-push only to your own feature branch: `git push -f origin feat/my-feature`

## Commit Frequency

- **Sweet spot**: One logical change per commit
- **Too frequent**: Many tiny changes that should be squashed
- **Too rare**: Multiple unrelated changes in one commit

Examples:

```bash
# Good: Each commit is logically complete
git log --oneline
6a3b2c1 docs: add API reference for user endpoints
5f4e3d2 test: add coverage for edge cases in token refresh
4c2b1a0 feat(auth): implement JWT token refresh
3a1b0c9 refactor(auth): extract validation logic to separate module

# Bad: Too granular
git log --oneline
9z8y7x6 fix typo in comment
8y7x6w5 remove unused import
7x6w5v4 add blank line
6w5v4u3 feat: add JWT token refresh

# Bad: Too coarse
git log --oneline
2b1a0z9 feat: add JWT refresh, fix API bugs, refactor auth, improve docs
```

## Tools & Integration

- **Pre-commit hooks**: Validate commit format before allowing commit
- **CI/CD**: Enforce commit message format in pull request checks
- **Changelog generation**: Use git-cliff to auto-generate CHANGELOG from commits

See `governance/quality-gates/README.md` for pre-commit hook configuration.
