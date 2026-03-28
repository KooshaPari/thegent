# GitHub Actions Workflow Templates — Complete Index

Complete reference for all CI/CD workflow templates in the Phenotype ecosystem.

**Location**: `/Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/`

## Quick Navigation

| Need | File | Read Time |
|------|------|-----------|
| Get started in 30 sec | `QUICK_START.md` | 2 min |
| Full setup & config | `README.md` | 10 min |
| Roll out across 50+ repos | `ADOPTION.md` | 5 min |
| This index | `INDEX.md` | 2 min |

## Billing / merge gate policy

- Treat billing failures on GitHub-hosted macOS/Windows runners as expected noise.
- Use repo-local pre-push hooks or commands as the merge gate.
- Keep long-term parity checks on self-hosted or developer-local runners.
- Do not make billed runner availability a dependency for PR merge readiness.

## Templates

### 1. rust-ci.yml
**Purpose**: Rust workspace CI  
**When**: Any repo with `Cargo.toml`  
**Checks**: fmt, clippy (strict), cargo test  
**Runner**: ubuntu-latest  
**Lines**: 22  
**Caching**: Swatinem/rust-cache@v2  

```bash
cp scripts/workflows/rust-ci.yml .github/workflows/
```

### 2. typescript-ci.yml
**Purpose**: TypeScript/Bun CI  
**When**: TypeScript projects with Bun runtime  
**Checks**: bun install (frozen), @biomejs/biome check, build, test  
**Runner**: ubuntu-latest  
**Lines**: 19  
**Caching**: Built into Bun  

```bash
cp scripts/workflows/typescript-ci.yml .github/workflows/
```

### 3. go-ci.yml
**Purpose**: Go module CI  
**When**: Any repo with `go.mod`  
**Checks**: go vet, go build, go test -race  
**Runner**: ubuntu-latest  
**Lines**: 19  
**Caching**: Native Go module caching  

```bash
cp scripts/workflows/go-ci.yml .github/workflows/
```

### 4. codeql.yml
**Purpose**: Security scanning (SAST)  
**When**: All repos (optional but recommended)  
**Checks**: Vulnerability detection, code quality patterns  
**Runner**: ubuntu-latest  
**Lines**: 24  
**Frequency**: Weekly + on PR/push  
**Configurable**: Language matrix (JS/TS, Python, Go, Java, C#, C++, etc.)  

```bash
cp scripts/workflows/codeql.yml .github/workflows/
# Edit matrix.language for your stack
```

### 5. sync-release-channels.yml
**Purpose**: (Pre-existing) Release channel synchronization  
**Status**: Already in directory  
**Lines**: 82  

## Documentation

### README.md
**Complete reference guide**
- Setup instructions (copy-paste and automated)
- Customization examples for each stack
- Troubleshooting guide
- Design decisions and rationale
- Billing constraint explanation
- Reference links

**Sections**:
1. Billing constraint overview
2. Template descriptions
3. Installation guide
4. Key design decisions
5. Troubleshooting
6. References

### QUICK_START.md
**Fast setup guide**
- 30-second setup instructions
- Which template for each stack
- Multi-stack repos
- Quick customizations
- Billing notes

**Intended for**: New users, quick copy-paste

### ADOPTION.md
**Ecosystem rollout plan**
- Phase-by-phase rollout (Rust, TS, Go)
- Batch adoption commands
- Custom variants for special repos
- Timeline and metrics
- AgilePlus tracking integration

**Intended for**: Coordinating adoption across 50+ repos

## Billing Constraint (CRITICAL)

All templates enforce **ubuntu-latest ONLY**:
- ✓ Standard Linux runners (free tier, included)
- ✗ macOS runners (billed at 10x)
- ✗ Windows runners (billed at 2x)

**Expected behavior**:
- CI will fail with "spending limit exceeded" on billed runners
- This is **normal and expected** per governance
- Do NOT block merges on billing failures
- Verify quality locally instead

Reference: `~/.claude/CLAUDE.md` — "GitHub Actions Billing Constraint"

## Usage Patterns

### Pattern 1: Single-Stack Repo
```bash
cd my-rust-project
mkdir -p .github/workflows
cp scripts/workflows/rust-ci.yml .github/workflows/
cp scripts/workflows/codeql.yml .github/workflows/
git add .github/workflows && git commit -m "chore: add CI workflows"
```

### Pattern 2: Multi-Stack Repo (TS + Go)
```bash
cd my-monorepo
mkdir -p .github/workflows
cp scripts/workflows/typescript-ci.yml .github/workflows/
cp scripts/workflows/go-ci.yml .github/workflows/
cp scripts/workflows/codeql.yml .github/workflows/
git add .github/workflows && git commit -m "chore: add CI workflows"
```

### Pattern 3: Batch Adoption (10+ repos)
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos
for repo in phenotype-xdd hexagon-rs go-hex; do
  cd $repo
  mkdir -p .github/workflows
  cp ../scripts/workflows/{rust,codeql}-ci.yml .github/workflows/ 2>/dev/null
  cp ../scripts/workflows/{typescript,codeql}-ci.yml .github/workflows/ 2>/dev/null
  cp ../scripts/workflows/{go,codeql}-ci.yml .github/workflows/ 2>/dev/null
  git add .github/workflows && git commit -m "chore: add CI workflows"
done
```

## Customization Quick Reference

### Rust: Allow warnings instead of strict
**File**: `.github/workflows/rust-ci.yml`
```yaml
# Change this:
run: cargo clippy --workspace --all-targets -- -D warnings
# To this:
run: cargo clippy --workspace --all-targets
```

### TypeScript: Add integration tests
**File**: `.github/workflows/typescript-ci.yml`
```yaml
- run: bun test
# Add this:
- run: bun test:integration
```

### Go: Add coverage
**File**: `.github/workflows/go-ci.yml`
```yaml
- run: go test ./... -race
# Change to:
- run: go test ./... -race -coverprofile=coverage.out
```

### CodeQL: Add Python scanning
**File**: `.github/workflows/codeql.yml`
```yaml
# Change this:
language: [javascript-typescript]
# To this:
language: [javascript-typescript, python]
```

## File Manifest

| File | Purpose | Lines | Updated |
|------|---------|-------|---------|
| rust-ci.yml | Rust CI | 22 | 2026-03-25 |
| typescript-ci.yml | TypeScript CI | 19 | 2026-03-25 |
| go-ci.yml | Go CI | 19 | 2026-03-25 |
| codeql.yml | Security | 24 | 2026-03-25 |
| sync-release-channels.yml | Release sync | 82 | 2024-03-24 |
| README.md | Full guide | 343 | 2026-03-25 |
| QUICK_START.md | Quick setup | ~75 | 2026-03-25 |
| ADOPTION.md | Rollout plan | ~200 | 2026-03-25 |
| INDEX.md | This file | ~250 | 2026-03-25 |

**Total**: ~1000 lines of workflow templates + documentation

## Validation Checklist

Before using in a repo:

- [ ] Read `QUICK_START.md` (2 min)
- [ ] Copy appropriate `.yml` file(s)
- [ ] Verify `go.mod`, `Cargo.toml`, or `package.json` exists
- [ ] Run local quality checks:
  - Rust: `cargo fmt --check && cargo clippy && cargo test`
  - TS: `bun install --frozen-lockfile && bunx @biomejs/biome check . && bun test`
  - Go: `go vet ./... && go build ./... && go test ./... -race`
- [ ] Commit and push
- [ ] Create PR
- [ ] Merge (expect CI billing failure, ignore)

## Troubleshooting Quick Links

| Problem | Solution | File |
|---------|----------|------|
| "Which template?" | QUICK_START.md, Table 1 | QUICK_START.md |
| "How to customize?" | Examples section | README.md |
| "Billing error?" | Expected behavior | README.md § Billing Constraint |
| "Roll out 50 repos?" | Phase-by-phase | ADOPTION.md |
| "Specific error?" | Troubleshooting | README.md § Troubleshooting |

## Integration with AgilePlus

Track workflow adoption in AgilePlus:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify --title "Add GitHub Actions CI workflows" \
  --description "Standardize CI/CD across Phenotype ecosystem"

# Update status per phase:
agileplus status ci-workflows --wp rust-adoption --state in-progress
agileplus status ci-workflows --wp typescript-adoption --state in-progress
agileplus status ci-workflows --wp go-adoption --state in-progress
```

## Design Decisions (Why These Choices?)

See `README.md § Key Design Decisions` for:
- Why ubuntu-only (billing constraint + free tier)
- Why Biome over ESLint (speed + formatting)
- Why single job per workflow (simplicity)
- Why native caching (performance)
- Why CodeQL (native GitHub integration, no cost)

## Reference Documents

- **Billing**: `~/.claude/CLAUDE.md` (GitHub Actions Billing Constraint)
- **Governance**: `~/.claude/AGENTS.md` (Global agent contract)
- **CI Policy**: `/Users/kooshapari/CodeProjects/Phenotype/CLAUDE.md` (CI Completeness Policy)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-25 | Initial release: rust-ci, typescript-ci, go-ci, codeql, docs |

## Support

For questions:
1. Check `README.md` (comprehensive)
2. Check `QUICK_START.md` (common cases)
3. Check `ADOPTION.md` (rollout questions)
4. Review individual `.yml` files (implementation details)
5. Reference governance docs (policy questions)

---

**Last updated**: 2026-03-25  
**Maintainer**: Phenotype Engineering Team  
**Repository**: `/Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/`
