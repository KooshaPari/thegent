# Workflow Template Adoption Plan

Guide for rolling out standardized CI workflows across the Phenotype ecosystem.

## High-Level Approach

1. **Individual Repos** — Add templates to `.github/workflows/` via PR
2. **Verify Locally** — Run repo-local pre-push checks before merge (CI billing failures are expected)
3. **Rollout** — Stacked PRs per repo type (Rust, TypeScript, Go)
4. **Coordination** — Use AgilePlus to track adoption across 50+ repos

## Permanent Handling Strategy

- GitHub-hosted macOS/Windows CI is not part of the merge gate for this account.
- The merge gate is the repo-local pre-push command or hook.
- If a repo needs runner parity, prefer a self-hosted or developer-local runner.
- Keep expensive or billing-sensitive checks out of GitHub-hosted required status checks.
- Make the local gate explicit in repo docs and hook scripts so the policy survives runner outages and billing resets.

## Adoption Sequence (By Stack)

### Phase 1: Rust Ecosystem (Week 1)

**Repos to target** (Rust workspaces):
- `phenotype-xdd` — Core lib
- `hexagon-rs` — Rust reference impl
- `phenotype-infrakit` — Infrastructure
- `phenotype-dep-guard` — Dependency analysis
- `phenotype-logger` — Logging
- `phenotype-metrics` — Metrics
- Other `*-rs` crates

**Batch command**:
```bash
#!/bin/bash
for repo in phenotype-xdd hexagon-rs phenotype-infrakit; do
  cd /Users/kooshapari/CodeProjects/Phenotype/repos/$repo
  mkdir -p .github/workflows
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/rust-ci.yml .github/workflows/
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/
  git add .github/workflows/
  git commit -m "chore: add GitHub Actions CI workflows

- rust-ci: format, lint, test
- codeql: security scanning

See: repos/scripts/workflows/README.md"
  git push origin fix/ci-workflows
done
```

### Phase 2: TypeScript Ecosystem (Week 1-2)

**Repos to target** (Bun/Node projects):
- `phenotype-agent-core` — Agent SDK
- `phenotype-auth-ts` — Auth library
- `phenotype-config-ts` — Config management
- `heliosApp` — Desktop app
- `thegent` — Dev tools
- Other TypeScript packages

**Batch command**:
```bash
#!/bin/bash
for repo in phenotype-agent-core phenotype-auth-ts heliosApp thegent; do
  cd /Users/kooshapari/CodeProjects/Phenotype/repos/$repo
  mkdir -p .github/workflows
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/typescript-ci.yml .github/workflows/
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/
  git add .github/workflows/
  git commit -m "chore: add GitHub Actions CI workflows

- typescript-ci: biome check, build, test
- codeql: security scanning

See: repos/scripts/workflows/README.md"
  git push origin fix/ci-workflows
done
```

### Phase 3: Go Ecosystem (Week 2)

**Repos to target** (Go modules):
- `go-hex` — Go reference impl
- `phenotype-go-kit` — Go toolkit
- `phenotype-go-auth` — Go auth
- Other `*-go` packages

**Batch command**:
```bash
#!/bin/bash
for repo in go-hex phenotype-go-kit phenotype-go-auth; do
  cd /Users/kooshapari/CodeProjects/Phenotype/repos/$repo
  mkdir -p .github/workflows
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/go-ci.yml .github/workflows/
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/codeql.yml .github/workflows/
  git add .github/workflows/
  git commit -m "chore: add GitHub Actions CI workflows

- go-ci: vet, build, test (with race detector)
- codeql: security scanning

See: repos/scripts/workflows/README.md"
  git push origin fix/ci-workflows
done
```

### Phase 4: Multi-Stack & Mixed (Week 3)

**Repos with multiple stacks**:
- Add ALL applicable workflows
- Example (Monorepo with TS + Go):
  ```bash
  cp typescript-ci.yml .github/workflows/
  cp go-ci.yml .github/workflows/
  cp codeql.yml .github/workflows/
  ```

### Phase 5: Verification & Cleanup (Week 3-4)

1. **Verify locally** in each repo:
   ```bash
   # Rust
   cargo fmt --check && cargo clippy --workspace && cargo test
   
   # TypeScript
   bun install --frozen-lockfile && bunx @biomejs/biome check . && bun test
   
   # Go
   go vet ./... && go build ./... && go test ./... -race
   ```

2. **Open PRs** in GitHub:
   ```bash
   gh pr create --title "chore: add GitHub Actions CI workflows" \
     --body "Standardized CI/CD using ecosystem templates.
   
   - rust-ci.yml for format/lint/test
   - typescript-ci.yml for biome/build/test
   - go-ci.yml for vet/build/test
   - codeql.yml for security scanning
   
   See: repos/scripts/workflows/README.md"
   ```

3. **Merge** once verified locally (CI will fail on billing, that's expected)

4. **Track** adoption in AgilePlus:
   ```bash
   cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
   agileplus status workflow-adoption --wp rust-batch --state complete
   agileplus status workflow-adoption --wp typescript-batch --state complete
   agileplus status workflow-adoption --wp go-batch --state complete
   ```

## Custom Variants (If Needed)

Some repos may need adjusted workflows:

### For monorepos with multiple workspaces (Rust)
```yaml
- name: test
  run: |
    cargo test --workspace
    cargo test --release --workspace
```

### For TypeScript with integration tests
```yaml
- run: bun test
- run: bun test:integration
```

### For Go with coverage
```yaml
- run: go test ./... -race -cover -coverprofile=coverage.out
- run: go tool cover -html=coverage.out
```

### For CodeQL with multiple languages
```yaml
strategy:
  matrix:
    language: [javascript-typescript, python, go]
```

## Expected CI Failures (Normal & Expected)

Due to GitHub Actions billing constraints:

1. **Jobs fail immediately** with "Spending limit exceeded" — ignore
2. **Do NOT wait** for CI to pass
3. **Verify locally** before merge
4. **Do NOT block PRs** on billing-caused failures
5. **Merge confidently** if local checks pass

This is intentional per Phenotype governance.

## Verification Checklist

For each repo after workflow addition:

- [ ] `.github/workflows/` directory created
- [ ] All applicable `.yml` files copied
- [ ] Local `cargo fmt/test`, `bun test`, `go test` all pass
- [ ] PR created with standardized commit message
- [ ] README.md linked in PR description
- [ ] Local verification step documented in PR
- [ ] PR merged (expecting CI failure on billing, not blocking merge)
- [ ] Status updated in AgilePlus

## Rollout Timeline

| Phase | Duration | Repos | Status |
|-------|----------|-------|--------|
| Rust Ecosystem | 3 days | 8-12 repos | Ready |
| TypeScript Ecosystem | 3-4 days | 10-15 repos | Ready |
| Go Ecosystem | 2 days | 5-8 repos | Ready |
| Multi-Stack & Cleanup | 4 days | All remaining | Ready |
| **Total** | **~2 weeks** | **50+ repos** | In Progress |

## Success Metrics

- [ ] 100% of Rust repos have rust-ci.yml
- [ ] 100% of TypeScript repos have typescript-ci.yml
- [ ] 100% of Go repos have go-ci.yml
- [ ] 100% of repos have codeql.yml
- [ ] All workflows added via PR with audit trail
- [ ] Local verification done before each merge
- [ ] Zero CI-blocking issues (billing failures are expected)

## Questions?

Refer to:
1. `README.md` — Full configuration guide
2. `QUICK_START.md` — 30-second setup
3. Individual `.yml` files — Implementation details
4. Phenotype governance (`~/.claude/CLAUDE.md`) — Billing policy

## Post-Adoption

Once all repos have workflows:

1. **Maintain** — Update templates centrally in `scripts/workflows/`
2. **Notify** — Alert teams when templates are updated
3. **Sync** — Provide command to pull latest template versions
4. **Monitor** — Track which repos use which workflow versions

Example notification:
```bash
# Create PR in each repo to pull latest
for repo in phenotype-xdd hexagon-rs phenotype-agent-core; do
  cd /path/to/$repo
  cp /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/workflows/*.yml .github/workflows/
  git add .github/workflows/
  git commit -m "chore: update GitHub Actions CI workflow templates"
  git push origin chore/update-workflows
done
```
