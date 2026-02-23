# Documentation Standards for atomsAgent

## Overview

This document establishes standards for organizing documentation in the atomsAgent repository to prevent markdown creep and maintain a clean, navigable structure.

## Directory Structure

```
atomsAgent/
├── README.md                    # Project overview (root only)
├── CHANGELOG.md                 # Version history (root only)
├── CONTRIBUTING.md              # Contribution guidelines (root only)
├── AGENTS.md                    # OpenSpec instructions (root only)
├── CLAUDE.md                    # OpenSpec instructions (root only)
│
└── docs/
    ├── DOCUMENTATION_STANDARDS.md  # This file
    ├── sessions/                   # Session-specific work
    │   └── YYYY-MM-DD-description/
    │       ├── DAG.md              # Work breakdown
    │       ├── SPEC.md             # Specifications
    │       ├── STATE.md            # Progress tracking
    │       └── ...                 # Other session docs
    ├── archive/                    # Completed/historical work
    │   └── *.md                    # Archived documentation
    ├── architecture/               # Permanent architecture docs
    ├── api/                        # API documentation
    ├── guides/                     # How-to guides
    ├── research/                   # Research findings
    └── mkdocs/                     # MkDocs site
```

## Rules

### ✅ DO

1. **Keep root clean**: Only 5 files allowed in root (README, CHANGELOG, CONTRIBUTING, AGENTS, CLAUDE)
2. **Use docs/ for everything else**: All other markdown goes in docs/
3. **Session-based work**: Use `docs/sessions/YYYY-MM-DD-description/` for active work
4. **Archive completed work**: Move finished projects to `docs/archive/`
5. **Consolidate duplicates**: Merge similar documents instead of creating new ones
6. **Use descriptive names**: File names should clearly indicate content
7. **Update, don't duplicate**: Modify existing docs instead of creating `_v2`, `_new`, `_old` versions

### ❌ DON'T

1. **No markdown in src/**: Source code directory stays clean
2. **No markdown in tests/**: Test directory stays clean
3. **No markdown in migrations/**: Only SQL files in migrations/
4. **No version suffixes**: Don't create `file_v2.md`, `file_new.md`, `file_old.md`
5. **No generic suffixes**: Don't create `file_helper.md`, `file_utils.md`, `file_complete.md`
6. **No root clutter**: Don't create random .md files in root directory
7. **No duplicate concerns**: Don't split related content across multiple files

## File Organization Checklist

Before creating ANY new markdown file:

- [ ] Is this session-specific work? → Use `docs/sessions/YYYY-MM-DD-*/`
- [ ] Is this completed/historical? → Use `docs/archive/`
- [ ] Is this permanent documentation? → Use appropriate `docs/` subdirectory
- [ ] Does a similar file already exist? → Update existing instead of creating new
- [ ] Can I name this with a clear, single-purpose noun? → If no, reconsider
- [ ] Will future developers understand this file's purpose? → If no, rename

## Examples

### ✅ GOOD

```
docs/guides/database-migrations.md      # Clear purpose
docs/guides/deployment.md               # Clear purpose
docs/guides/warp-speed-development.md   # Clear purpose
docs/sessions/2025-11-25-feature-x/     # Date-based session
docs/archive/tier1-completion.md        # Archived work
```

### ❌ BAD

```
./WARP.md                               # Root clutter
./DEPLOYMENT_INSTRUCTIONS.md            # Root clutter
./TIER1_EXECUTION_GUIDE.md              # Root clutter
docs/guides/guide_helper.md             # Generic suffix
docs/guides/deployment_v2.md            # Version suffix
docs/guides/deployment_final.md         # Meaningless suffix
```

## Enforcement

Run this command to check for markdown creep:

```bash
# Find markdown files outside docs/
find . -name "*.md" -not -path "./docs/*" -not -path "./node_modules/*" \
  -not -path "./.git/*" -not -name "README.md" -not -name "CHANGELOG.md" \
  -not -name "CONTRIBUTING.md" -not -name "AGENTS.md" -not -name "CLAUDE.md"

# Should return empty or only allowed files
```

## Questions?

- **Session work**: Use `docs/sessions/YYYY-MM-DD-description/`
- **Completed work**: Move to `docs/archive/`
- **Permanent docs**: Use appropriate `docs/` subdirectory
- **Unsure**: Ask before creating new files

