# Distribution Automation Module

Distribution automation scripts for syncing governance files from thegent (source of truth) to consumer repositories.

## Scripts

### distribute.sh
Pushes governance files to a target repository.

**Usage:**
```bash
./distribute.sh <target-repo-path> [--force] [--no-backup]
```

**What it syncs:**
- `hooks/` — All governance hooks and quality gates
- `.pre-commit-config.yaml` — Pre-commit configuration
- `Taskfile.yml` — Task runner (unless customized)

**Features:**
- Respects local customizations (skips files with `.local-override` marker)
- Creates backups before overwriting
- Installs pre-commit hooks in target repository
- Interactive confirmation for each file (can be disabled with `--force`)

**Example:**
```bash
./distribute.sh ../../AgilePlus
./distribute.sh ../../phenotype-infrakit --force
```

### validate-sync.sh
Checks for governance drift in consumer repositories.

**Usage:**
```bash
./validate-sync.sh [consumer-repo-path] [--all] [--verbose]
```

**Features:**
- Compares consumer files against thegent source
- Reports missing or outdated files
- Suggests update commands for out-of-sync repos
- Can validate single repo or all known repos

**Example:**
```bash
./validate-sync.sh ../../AgilePlus
./validate-sync.sh --all --verbose
```

### bootstrap-project.sh
Full project initialization with thegent governance.

**Usage:**
```bash
./bootstrap-project.sh <project-path> [--stack <python|rust|go>]
```

**What it creates:**
- Git repository (if not present)
- Documentation site (VitePress via phenodocs)
- Governance infrastructure (hooks, pre-commit, Taskfile)
- Code quality linters for detected stack
- CLAUDE.md project instructions
- Documentation structure (guides, reference, reports)

**Features:**
- Auto-detects project stack from Cargo.toml, package.json, pyproject.toml, go.mod
- Creates directory structure if missing
- Installs pre-commit hooks
- Stack-specific linting configuration

**Example:**
```bash
./bootstrap-project.sh /path/to/new-project
./bootstrap-project.sh /path/to/rust-project --stack rust
```

## Configuration

### consumer-repos.txt
Lists known consumer repositories. Used by `validate-sync.sh --all` and Taskfile tasks.

Format: one repository path per line (can be relative to thegent root)

Example:
```
../../AgilePlus
../../phenotype-infrakit
../../heliosCLI
```

## Task Runner Integration

The Taskfile.distribute.yml provides convenient task-based access:

```bash
# Distribute to all known repos
task distribute:all

# Validate sync status
task distribute:validate

# Bootstrap new project
task bootstrap -- /path/to/project --stack python

# List known repos
task distribute:list

# Show status summary
task distribute:status
```

## Workflow Examples

### Update all consumer repos
```bash
task distribute:status              # Check current status
task distribute:backup              # Back up current state
task distribute:all -- --force      # Push updates
```

### Bootstrap new repository
```bash
task bootstrap -- /path/to/new-repo
cd /path/to/new-repo
git add -A
git commit -m "chore: bootstrap from thegent"
git push -u origin main
```

### Check drift in specific repo
```bash
task distribute:validate:target -- ../../AgilePlus
```

## Customization

### Local Overrides
To prevent a file from being overwritten by distribution scripts, add a `.local-override` comment:

```bash
# In target repo's hooks/governance-gates.sh:
# .local-override
# This file has custom local modifications

# rest of file...
```

The distribute script will skip files with this marker.

### Stack-Specific Linting
bootstrap-project.sh detects the project stack and configures appropriate linters:

- **Rust:** clippy + rustfmt
- **Python:** ruff (lint + format)
- **Go:** golangci-lint
- **TypeScript:** oxlint + prettier

To specify manually:
```bash
./bootstrap-project.sh /path --stack rust
```

## Troubleshooting

### "Not a git repository" error
Ensure target path is a valid git repository. Initialize if needed:
```bash
cd <target-path>
git init
```

### Pre-commit not found
Install pre-commit first:
```bash
pip install pre-commit
pre-commit install
```

### Drift detected but files look correct
Check for whitespace differences or line ending changes:
```bash
validate-sync.sh <repo> --verbose
```

### Backup directory cluttered
Old backups are timestamped. Clean up manually:
```bash
rm -rf <repo>/.backup.* <repo>/.governance-backup-*
```

## Future Enhancements

- [ ] Automatic drift detection and repair
- [ ] Selective file distribution (e.g., only hooks)
- [ ] Multi-branch distribution strategy
- [ ] Merge conflict resolution for customized files
- [ ] Distribution audit trail / change history
- [ ] GitHub Actions integration for automated sync

## See Also

- `Taskfile.distribute.yml` — Task runner definitions
- `hooks/` — Governance files being distributed
- `.pre-commit-config.yaml` — Pre-commit configuration source
- `docs/governance/` — Governance documentation
