# GitHub Actions Workflows — Quick Start

Fast setup guide for adding CI to any Phenotype ecosystem repo.

## 30-Second Setup

```bash
# 1. Navigate to your repo
cd /path/to/repo

# 2. Copy templates for your stack
# For Rust:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/rust-ci.yml .github/workflows/

# For TypeScript/Bun:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/typescript-ci.yml .github/workflows/

# For Go:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/go-ci.yml .github/workflows/

# 3. Add security scanning (all stacks)
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/

# 4. Commit and push
git add .github/workflows/
git commit -m "chore: add GitHub Actions CI workflows"
git push origin your-branch
```

## Permanent billing handling

- GitHub-hosted macOS/Windows checks are not part of the merge gate.
- Run the repo-local pre-push gate before opening or updating a PR.
- If CI reports a spending-limit or billing error, treat it as expected and verify locally instead.
- For parity checks, use a self-hosted or developer-local runner rather than a billed hosted runner.

## Which Template Do I Need?

```bash
# 1. Navigate to your repo
cd /path/to/repo

# 2. Copy templates for your stack
# For Rust:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/rust-ci.yml .github/workflows/

# For TypeScript/Bun:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/typescript-ci.yml .github/workflows/

# For Go:
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/go-ci.yml .github/workflows/

# 3. Add security scanning (all stacks)
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/

# 4. Commit and push
git add .github/workflows/
git commit -m "chore: add GitHub Actions CI workflows"
git push origin your-branch
```

## Which Template Do I Need?

| Stack | File | Requirements |
|-------|------|--------------|
| Rust | rust-ci.yml | `Cargo.toml` workspace |
| TypeScript | typescript-ci.yml | `package.json` + `bun.lockb` or `package-lock.json` |
| Go | go-ci.yml | `go.mod` file |
| Any | codeql.yml | GitHub repo (no local requirements) |

## Multi-Stack Repo?

Copy multiple templates:

```bash
# TypeScript backend + Go CLI
cp scripts/workflows/typescript-ci.yml .github/workflows/
cp scripts/workflows/go-ci.yml .github/workflows/
cp scripts/workflows/codeql.yml .github/workflows/
```

Each workflow runs independently on PR/push.

## Billing Notes

- All workflows use `ubuntu-latest` (standard Linux runner, free tier)
- No macOS or Windows runners (billed at 10x rate)
- If CI fails with "spending limit exceeded" — this is expected; verify quality locally
- Do NOT block merges on billing-caused CI failures

## What Gets Checked?

### Rust
```
✓ Code formatting (rustfmt)
✓ Linting (clippy)
✓ Unit tests
```

### TypeScript
```
✓ Dependencies frozen-lockfile check
✓ Code quality (Biome)
✓ TypeScript compilation
✓ Unit tests
```

### Go
```
✓ Code analysis (go vet)
✓ Compilation
✓ Unit tests with race detector
```

### CodeQL (All)
```
✓ Vulnerability detection
✓ Security patterns
✓ Code quality analysis
```

## Customization (2 min)

### Change Rust linter strictness
Edit `.github/workflows/rust-ci.yml`:
```yaml
- name: clippy
  run: cargo clippy --workspace --all-targets  # Remove -- -D warnings to allow warnings
```

### Change TypeScript test command
Edit `.github/workflows/typescript-ci.yml`:
```yaml
- run: bun test:integration  # Or your custom test script
```

### Change Go version
Edit `.github/workflows/go-ci.yml`:
```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'  # Pin version instead of go.mod
```

### Change CodeQL language
Edit `.github/workflows/codeql.yml`:
```yaml
strategy:
  matrix:
    language: [python]  # Or: [go], [java-kotlin], [cpp], [csharp], etc.
```

## Troubleshooting

### "Spending limit exceeded" error
Expected behavior. Verify locally:
```bash
cargo build && cargo test  # Rust
bun test                   # TypeScript
go test ./... && go vet    # Go
```

### "Frozen lockfile" error (TypeScript)
Update your lock file:
```bash
bun install  # Updates bun.lockb
git add bun.lockb && git commit -m "chore: update lockfile"
```

### CodeQL doesn't run
Check you have the right language:
```yaml
language: [javascript-typescript]  # For TS
language: [python]                # For Python
language: [go]                      # For Go
```

## Full Guide

See `README.md` in the same directory for:
- Complete customization examples
- Architecture decisions
- Design rationale
- Advanced configuration
