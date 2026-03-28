# =============================================================================
# Phenotype Pre-Push Hook Setup
# =============================================================================

## Quick Install

```bash
# For this repo
ln -sf ../../scripts/hooks/pre-push .git/hooks/pre-push

# For all repos (run from workspace root)
find . -name ".git" -type d -exec sh -c 'ln -sf ../../scripts/hooks/pre-push "$1/hooks/pre-push"' _ {} \;
```

## What It Does

The pre-push hook runs local quality checks before any push, replacing
billed GitHub Actions macOS/Windows CI gates.

## Skipping

```bash
# Skip all checks
SKIP_LOCAL_PREPUSH=1 git push

# Skip specific file types
SKIP_FILETYPES="*.test.js" git push
```

## Requirements

| Language | Tool Required |
|----------|---------------|
| Rust | `cargo` |
| TypeScript | `bun` or `npx` |
| Python | `python3` |
| Go | `go` |
| Shell | `shellcheck` |

## Philosophy

- **Local checks = merge gate**
- **GitHub Actions = validation/telemetry only**
- **Billing failures = expected, not blocking**
