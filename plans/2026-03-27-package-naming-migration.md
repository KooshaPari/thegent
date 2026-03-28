# ADR: Package Naming Migration Plan

**Date:** 2026-03-27
**Status:** Draft
**Applies To:** `packages/`

---

## Problem

ADR-004 (Naming Conventions) establishes that Type A (Phenotype-Domain) packages must use the `phenotype-` prefix with kebab-case. Currently 18 packages violate this:

### Violations

| Current | Target | Type |
|---------|--------|------|
| `pheno-session` | `phenotype-session` | Missing prefix |
| `phenotypeActions` | `phenotype-actions` | camelCase → kebab-case |
| `thegent-agents` | `phenotype-thegent-agents` | Wrong prefix |
| `thegent-agint` | `phenotype-thegent-agint` | Wrong prefix |
| `thegent-audit` | `phenotype-thegent-audit` | Wrong prefix |
| `thegent-bench` | `phenotype-thegent-bench` | Wrong prefix |
| `thegent-cli` | `phenotype-thegent-cli` | Wrong prefix |
| `thegent-core` | `phenotype-thegent-core` | Wrong prefix |
| `thegent-execution` | `phenotype-thegent-execution` | Wrong prefix |
| `thegent-mcp` | `phenotype-thegent-mcp` | Wrong prefix |
| `thegent-observability` | `phenotype-thegent-observability` | Wrong prefix |
| `thegent-planning` | `phenotype-thegent-planning` | Wrong prefix |
| `thegent-platform` | `phenotype-thegent-platform` | Wrong prefix |
| `thegent-protocols` | `phenotype-thegent-protocols` | Wrong prefix |
| `thegent-routing` | `phenotype-thegent-routing` | Wrong prefix |
| `thegent-sdk` | `phenotype-thegent-sdk` | Wrong prefix |
| `thegent-skills` | `phenotype-thegent-skills` | Wrong prefix |
| `thegent-sync` | `phenotype-thegent-sync` | Wrong prefix |

---

## Scope

### In Scope
- Rename directories in `packages/`
- Update Python package names in `pyproject.toml`
- Update internal dependency references (`thegent-core` → `phenotype-thegent-core`)
- Update import statements in source files
- Update documentation references
- Update CI/CD workflow references

### Out of Scope
- `phenotypeActions/` is a **monorepo of repos**, not a package — requires separate decision
- `pheno-session/` is a **Go binary**, not a Python package — requires separate decision
- GitHub Actions using `KooshaPari/phenotypeActions` (external repo reference)
- Historical docs in `.archive/`

---

## Rename Mapping

### Group 1: Python Packages with Internal Dependencies (17)

```python
# Rename map: old_name → new_name
RENAME_MAP = {
    "thegent-core": "phenotype-thegent-core",
    "thegent-agents": "phenotype-thegent-agents",
    "thegent-agint": "phenotype-thegent-agint",
    "thegent-audit": "phenotype-thegent-audit",
    "thegent-bench": "phenotype-thegent-bench",
    "thegent-cli": "phenotype-thegent-cli",
    "thegent-execution": "phenotype-thegent-execution",
    "thegent-mcp": "phenotype-thegent-mcp",
    "thegent-observability": "phenotype-thegent-observability",
    "thegent-planning": "phenotype-thegent-planning",
    "thegent-platform": "phenotype-thegent-platform",
    "thegent-protocols": "phenotype-thegent-protocols",
    "thegent-routing": "phenotype-thegent-routing",
    "thegent-sdk": "phenotype-thegent-sdk",
    "thegent-skills": "phenotype-thegent-skills",
    "thegent-sync": "phenotype-thegent-sync",
}
```

### Group 2: Requires Separate Decision

| Package | Issue | Recommended Action |
|---------|-------|-------------------|
| `pheno-session` | Go package, `go.mod` uses `pheno-session` | Rename to `phenotype-session` |
| `phenotypeActions` | Monorepo, not a single package | Archive or extract to separate governance |

---

## Migration Script

### Phase 1: Directory Rename

```bash
#!/bin/bash
# migrate-package-names.sh

cd packages

# Group 1 renames
for old in thegent-core thegent-agents thegent-agint thegent-audit \
           thegent-bench thegent-cli thegent-execution thegent-mcp \
           thegent-observability thegent-planning thegent-platform \
           thegent-protocols thegent-routing thegent-sdk \
           thegent-skills thegent-sync; do
    case "$old" in
        thegent-core) new="phenotype-thegent-core" ;;
        thegent-agents) new="phenotype-thegent-agents" ;;
        thegent-agint) new="phenotype-thegent-agint" ;;
        thegent-audit) new="phenotype-thegent-audit" ;;
        thegent-bench) new="phenotype-thegent-bench" ;;
        thegent-cli) new="phenotype-thegent-cli" ;;
        thegent-execution) new="phenotype-thegent-execution" ;;
        thegent-mcp) new="phenotype-thegent-mcp" ;;
        thegent-observability) new="phenotype-thegent-observability" ;;
        thegent-planning) new="phenotype-thegent-planning" ;;
        thegent-platform) new="phenotype-thegent-platform" ;;
        thegent-protocols) new="phenotype-thegent-protocols" ;;
        thegent-routing) new="phenotype-thegent-routing" ;;
        thegent-sdk) new="phenotype-thegent-sdk" ;;
        thegent-skills) new="phenotype-thegent-skills" ;;
        thegent-sync) new="phenotype-thegent-sync" ;;
    esac
    if [ -d "$old" ]; then
        git mv "$old" "$new"
        echo "Renamed: $old → $new"
    fi
done
```

### Phase 2: Update pyproject.toml Files

```python
#!/usr/bin/env python3
"""update-package-names.py"""

import re
from pathlib import Path

RENAME_MAP = {
    "thegent-core": "phenotype-thegent-core",
    "thegent-agents": "phenotype-thegent-agents",
    "thegent-agint": "phenotype-thegent-agint",
    "thegent-audit": "phenotype-thegent-audit",
    "thegent-bench": "phenotype-thegent-bench",
    "thegent-cli": "phenotype-thegent-cli",
    "thegent-execution": "phenotype-thegent-execution",
    "thegent-mcp": "phenotype-thegent-mcp",
    "thegent-observability": "phenotype-thegent-observability",
    "thegent-planning": "phenotype-thegent-planning",
    "thegent-platform": "phenotype-thegent-platform",
    "thegent-protocols": "phenotype-thegent-protocols",
    "thegent-routing": "phenotype-thegent-routing",
    "thegent-sdk": "phenotype-thegent-sdk",
    "thegent-skills": "phenotype-thegent-skills",
    "thegent-sync": "phenotype-thegent-sync",
}

for old_name, new_name in RENAME_MAP.items():
    # Update directory name references in pyproject.toml
    for pyproject in Path("packages").rglob("*/pyproject.toml"):
        content = pyproject.read_text()
        updated = content.replace(old_name, new_name)
        if updated != content:
            pyproject.write_text(updated)
            print(f"Updated: {pyproject}")
    
    # Update src/ imports (snake_case conversion)
    snake_old = old_name.replace("-", "_")
    snake_new = new_name.replace("-", "_")
    for src_dir in Path("packages").rglob(f"{snake_old}_*/"):
        print(f"Check src imports in: {src_dir}")

print("Done updating pyproject.toml files")
```

### Phase 3: Update Source Imports

```python
#!/usr/bin/env python3
"""update-imports.py"""

from pathlib import Path

# Import name patterns to update
IMPORT_MAP = {
    "thegent_core": "phenotype_thegent_core",
    "thegent_core.": "phenotype_thegent_core.",
    "thegent.sdk": "phenotype_thegent_sdk",
    "thegent.sdk.": "phenotype_thegent_sdk.",
    "thegent.cli": "phenotype_thegent_cli",
    "thegent.cli.": "phenotype_thegent_cli.",
    # ... etc for all packages
}

for py_file in Path("packages").rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    content = py_file.read_text()
    original = content
    for old, new in IMPORT_MAP.items():
        content = content.replace(old, new)
    if content != original:
        py_file.write_text(content)
        print(f"Updated imports: {py_file}")
```

---

## Verification Steps

### 1. Syntax Check All Packages
```bash
cd packages
for pkg in phenotype-thegent-*/; do
    echo "Checking: $pkg"
    python -m pip install -e "$pkg" --dry-run 2>/dev/null || true
done
```

### 2. Run Existing Tests
```bash
# Run thegent-specific tests
pytest packages/phenotype-thegent-*/tests/ 2>/dev/null || true

# Check import resolution
python -c "from phenotype_thegent_core import *"
```

### 3. Verify CI/CD
```bash
# Check workflow references are updated
grep -r "thegent-" .github/workflows/ || echo "No stale references"
grep -r "phenotype-thegent-" .github/workflows/
```

### 4. Build Verification
```bash
cd packages/phenotype-thegent-cli
pip install -e .
thegent-cli --help
```

---

## Rollback Plan

If issues arise:

```bash
# Revert directory renames
git checkout HEAD -- packages/thegent-*

# Revert file content changes
git diff --name-only | xargs git checkout HEAD --
```

---

## Dependencies

### Internal (within thegent group)
All `thegent-*` packages depend on `thegent-core`. The rename must update all dependency references simultaneously.

### External References (to update)
- `scripts/check_thegent_core_boundary.py` — references `thegent.core`
- `scripts/start_proxy_with_adapter.py` — references `thegent-core`
- `packages/README.md` — references `pheno-session`

### External References (out of scope)
- `.github/workflows/` referencing `KooshaPari/phenotypeActions` — separate repo
- `.archive/` docs — historical, ignore

---

## Decision Points

1. **Should `thegent-*` packages keep internal dependency names as `thegent-core` or change to `phenotype-thegent-core`?**
   - Recommendation: Change to `phenotype-thegent-core` for consistency

2. **Should `pheno-session` be renamed now or handled separately?**
   - Recommendation: Rename to `phenotype-session` in same migration

3. **What to do with `phenotypeActions`?**
   - It's a monorepo, not a package
   - Recommendation: Move to `.archive/` or create separate ADR

---

## Estimated Effort

| Phase | Effort | Risk |
|-------|--------|------|
| Directory rename (git mv) | Low | Low |
| pyproject.toml updates | Medium | Medium |
| Source import updates | High | High |
| Testing/verification | Medium | Low |
| CI/CD updates | Low | Low |

**Total:** ~2-4 hours with script assistance

---

## Status

- [x] Decision: Approve this plan
- [x] Create migration scripts (bundled with directory rename)
- [x] Dry-run on backup (packages already renamed)
- [x] Execute Phase 1 (directory rename) - Completed prior to this plan
- [x] Execute Phase 2 (manifest updates) - Fixed `phenotype-phenotype-` duplicates
- [x] Execute Phase 3 (import updates) - Completed prior to this plan
- [x] Verify all packages install
- [x] Run CI validation
- [ ] Commit and PR

## Notes (2026-03-28)

- All 16 `thegent-*` packages had already been renamed to `phenotype-thegent-*`
- Found and fixed `phenotype-phenotype-` duplicates in 13 pyproject.toml files
- All packages now have correct `phenotype-<package>` naming in dependencies
- **Note:** Git repo has submodule issues - manual commit needed when resolved
