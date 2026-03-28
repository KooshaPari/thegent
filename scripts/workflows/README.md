# GitHub Actions Workflow Templates

Local-first CI/CD workflow templates for the Phenotype ecosystem. All templates use `ubuntu-latest` (standard Linux runners) and treat GitHub-hosted macOS/Windows jobs as unsupported in this account.

## Billing Constraint

**CRITICAL**: The KooshaPari GitHub account has persistent Actions billing/spending-limit issues.
- All workflows use **standard Linux runners only** (ubuntu-latest)
- **Never** use macOS (`macos-latest`) or Windows (`windows-latest`) runners
- GitHub Actions CI jobs will fail immediately with billing errors on non-standard runners
- Local pre-push checks are the merge gate; GitHub Actions is validation/telemetry, not the source of truth
- If a repo needs parity checks, use self-hosted or developer-local runners, not billed GitHub-hosted macOS/Windows jobs
- Do NOT block merges on CI failures caused by billing — verify quality locally instead

## Permanent local-first operating model

For every repo in this ecosystem:
- keep the authoritative checks in repo-local scripts or hooks
- run the repo's local pre-push gate before opening or updating a PR
- keep GitHub Actions limited to ubuntu-latest checks and optional security scanning
- treat billed runner failures as expected infrastructure noise, not merge blockers
- codify the rule in docs and scripts so it remains true when GitHub billing changes or runners are temporarily unavailable

## Templates


### 1. rust-ci.yml — Rust Workspace CI

**Use when**: Repository contains Rust code with workspace support.

**Runs on**: ubuntu-latest

**Checks**:
- `cargo fmt --check` — Code formatting (rustfmt)
- `cargo clippy` — Linting with treat-warnings-as-errors
- `cargo test --workspace` — Unit tests

**Setup**:
```bash
# Copy to .github/workflows/
cp scripts/workflows/rust-ci.yml .github/workflows/

# Or create custom variant
cat > .github/workflows/rust-ci.yml << 'YAML'
name: Rust CI
on: [pull_request, push: {branches: [main]}]
jobs:
  ci:
    runs-on: ubuntu-latest
    # ... (see rust-ci.yml for full content)
YAML
```

**Customization**:
- Modify `cargo clippy` arguments to adjust lint strictness
- Add `--release` flag to `cargo test` for performance testing
- Add additional workspaces with multiple `cargo` commands

---

### 2. typescript-ci.yml — TypeScript/Bun CI

**Use when**: Repository uses TypeScript with Bun runtime.

**Runs on**: ubuntu-latest

**Checks**:
- `bun install --frozen-lockfile` — Dependency verification
- `bunx @biomejs/biome check` — Linting and formatting with Biome
- `bun run build` — TypeScript compilation
- `bun test` — Unit tests

**Setup**:
```bash
# Copy to .github/workflows/
cp scripts/workflows/typescript-ci.yml .github/workflows/

# Ensure package.json has build and test scripts
cat package.json | grep -A2 '"scripts"'
# Should include: "build", "test"
```

**Customization**:
- Change `bun-version: latest` to pin a specific version (e.g., `1.1.0`)
- Replace Biome with alternative: `bunx eslint . && bunx prettier --check .`
- Add coverage check: `bun test --coverage`
- Add integration tests: add separate `- run: bun test:integration` step

---

### 3. go-ci.yml — Go CI

**Use when**: Repository contains Go modules (`go.mod`).

**Runs on**: ubuntu-latest

**Checks**:
- `go vet ./...` — Code analysis and type checking
- `go build ./...` — Compilation
- `go test ./... -race` — Unit tests with race detector

**Setup**:
```bash
# Copy to .github/workflows/
cp scripts/workflows/go-ci.yml .github/workflows/

# Verify go.mod exists
ls -la go.mod
```

**Customization**:
- Add `go mod tidy` check before build
- Add coverage check: `go test ./... -cover -coverprofile=coverage.out`
- Add golangci-lint: add step with `golangci/golangci-lint-action@v4`
- Pin Go version in `actions/setup-go@v5` with `go-version: '1.22'`

---

### 4. codeql.yml — Security Scanning

**Use when**: Any repository needs SAST (Static Application Security Testing).

**Runs on**: ubuntu-latest

**Checks**:
- CodeQL analysis for configured language(s)
- Vulnerability detection
- Scheduled runs (weekly on Mondays at 12:00 UTC)

**Setup**:
```bash
# Copy to .github/workflows/
cp scripts/workflows/codeql.yml .github/workflows/

# Edit matrix.language for your repo type:
# - javascript-typescript  (JS/TS/Node)
# - python                  (Python)
# - go                       (Go)
# - java-kotlin             (Java/Kotlin)
# - csharp                  (C#)
# - cpp                      (C/C++)
```

**Customization** (per repo):

**TypeScript repo**:
```yaml
strategy:
  matrix:
    language: [javascript-typescript]
```

**Python repo**:
```yaml
strategy:
  matrix:
    language: [python]
```

**Multi-language repo**:
```yaml
strategy:
  matrix:
    language: [javascript-typescript, python, go]
```

**Go repo with custom build**:
```yaml
strategy:
  matrix:
    language: [go]
steps:
  # ... standard steps ...
  - name: Build
    run: |
      go build ./...
      go build ./cmd/...
```

---

## Installation Guide

### Option A: Copy Individual Templates

```bash
cd /path/to/your/repo

# For Rust projects
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/rust-ci.yml .github/workflows/

# For TypeScript projects
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/typescript-ci.yml .github/workflows/

# For Go projects
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/go-ci.yml .github/workflows/

# For security scanning (all projects)
cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/
```

### Option B: Setup Script

Create `scripts/setup-ci.sh` in your repo:

```bash
#!/bin/bash
set -e

TEMPLATES_DIR="/Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows"
TARGET_DIR=".github/workflows"

mkdir -p "$TARGET_DIR"

# Detect repo type and copy appropriate template
if [ -f "Cargo.toml" ]; then
  echo "Detecting Rust workspace..."
  cp "$TEMPLATES_DIR/rust-ci.yml" "$TARGET_DIR/"
fi

if [ -f "bun.lockb" ] || grep -q '"scripts"' package.json 2>/dev/null; then
  echo "Detecting TypeScript/Bun project..."
  cp "$TEMPLATES_DIR/typescript-ci.yml" "$TARGET_DIR/"
fi

if [ -f "go.mod" ]; then
  echo "Detecting Go module..."
  cp "$TEMPLATES_DIR/go-ci.yml" "$TARGET_DIR/"
fi

# Always add security scanning
cp "$TEMPLATES_DIR/codeql.yml" "$TARGET_DIR/"

echo "CI workflows installed to $TARGET_DIR"
git add "$TARGET_DIR"
git commit -m "chore: add GitHub Actions CI workflows"
```

Run with:
```bash
bash scripts/setup-ci.sh
```

---

## Key Design Decisions

### 1. Ubuntu-Only (Billing Constraint)

All templates use `runs-on: ubuntu-latest` because:
- Standard Linux runners are included in GitHub Actions free tier
- macOS and Windows runners are billed at 10x rate
- The account has persistent billing issues; no billed runners are permitted
- Quality can be verified locally on developer machines before merge

### 2. Single Job per Workflow

Each workflow has one job (`ci:`) that:
- Runs all checks sequentially
- Fails fast on first error
- Avoids parallel job overhead
- Simplifies troubleshooting

### 3. Caching

- **Rust**: `Swatinem/rust-cache@v2` — Caches `target/` directory
- **Go**: `actions/setup-go@v5` with `cache: true` — Auto-caches modules
- **Bun**: `bun install --frozen-lockfile` — Uses lock file, no cache needed

### 4. Modern Tooling

- **Rust**: `dtolnay/rust-toolchain@stable` — Latest stable Rust + components
- **TypeScript**: Bun runtime + Biome (faster than ESLint/Prettier combo)
- **Go**: Standard `go` commands + race detector
- **Security**: GitHub's native CodeQL (no extra cost, deep analysis)

---

## Troubleshooting

### CI Fails with "Billing/Spending Limit" Error

**Cause**: Job tried to run on macOS or Windows runner (even if workflow file says ubuntu-latest, check branch protection rules).

**Fix**:
1. Verify workflow file uses `ubuntu-latest`
2. Check `.github/settings.json` or branch protection rules — remove macOS/Windows requirements
3. Merge locally if CI cannot run due to billing

### "Frozen Lockfile" Error (TypeScript)

**Cause**: `package-lock.json` or `bun.lockb` is out of sync with `package.json`.

**Fix**:
```bash
bun install  # Updates lock file
git add bun.lockb package.json
git commit -m "chore: update lockfile"
```

### Clippy Warnings Treated as Errors (Rust)

**Cause**: `-D warnings` flag converts all warnings to hard errors.

**Fix** (if legitimate):
```rust
#[allow(clippy::rule_name)]
fn my_function() { ... }
```

Or relax in workflow:
```yaml
- name: clippy
  run: cargo clippy --workspace --all-targets  # Remove -- -D warnings
```

### CodeQL Language Not Detected

**Cause**: Language matrix doesn't match actual repo code.

**Fix**:
```yaml
strategy:
  matrix:
    language: [javascript-typescript, python]  # Add your languages
```

---

## References

- [Rust Toolchain Action](https://github.com/dtolnay/rust-toolchain)
- [Setup Bun Action](https://github.com/oven-sh/setup-bun)
- [Setup Go Action](https://github.com/actions/setup-go)
- [CodeQL Action](https://github.com/github/codeql-action)
- [Biome Linter](https://biomejs.dev/)
- [GitHub Actions Billing](https://docs.github.com/en/billing/managing-billing-for-github-actions)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-25 | Initial templates: rust-ci, typescript-ci, go-ci, codeql |

---

## Contributing

To update templates:
1. Edit the file in `scripts/workflows/`
2. Test locally in a test repository
3. Commit with message: `chore: update CI workflow templates`
4. Notify Phenotype ecosystem teams for adoption
