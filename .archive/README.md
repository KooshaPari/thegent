# Archive: Duplicate Test Files and Components

This directory contains duplicate files that were archived to reduce disk space waste and prevent agent confusion.

## Rationale

During a workspace LOC audit (2026-03-29), approximately 35,000 lines of duplicated test files and components were identified across worktrees. These duplicates waste disk space and create confusion when multiple agents edit the same logic in different locations.

Per the **Phenotype Long-Term Stability and Non-Destructive Change Protocol**, duplicates are moved to `.archive/` rather than deleted, preserving them for reference while eliminating active confusion.

## Contents

### duplicate-tests/
- **test_phench_runtime.py** (2,116 lines)
  - Duplicate of canonical copy at: `/platforms/thegent/tests/test_phench_runtime.py`
  - Tests phench runtime behavior
  - Archived from worktree to prevent duplicate editing

- **test_unit_cli_coverage_c.py** (2,466 lines)
  - Duplicate of canonical copy at: `/platforms/thegent/tests/test_unit_cli_coverage_c.py`
  - CLI unit test coverage
  - Archived from worktree to prevent duplicate editing

### duplicate-components/
- **sidebar-auto.ts** (6,764 lines)
  - Duplicate of canonical copy at: `/platforms/thegent/docs/.vitepress/sidebar-auto.ts`
  - VitePress documentation sidebar auto-generation
  - Archived from worktree to prevent duplicate editing

- **api.ts** (805 lines)
  - Duplicate of canonical copy at: `/platforms/thegent/apps/byteport/frontend/web-next/lib/api.ts`
  - API client library
  - Archived from worktree to prevent duplicate editing

## Total LOC Archived

- Python test files: 4,582 lines
- TypeScript components: 7,569 lines
- **Total: 12,151 lines** (reduced agent confusion surface in this worktree)

## Canonical Locations

All active development should reference these canonical locations:
- Test files: `/platforms/thegent/tests/`
- Documentation config: `/platforms/thegent/docs/.vitepress/`
- API library: `/platforms/thegent/apps/byteport/frontend/web-next/lib/`

## Recovery

If you need to reference or recover archived files, they remain intact in this directory. To restore, copy back to the original location with appropriate rebasing against the canonical version.

---
**Archived:** 2026-03-29
**Policy:** Phenotype Long-Term Stability and Non-Destructive Change Protocol
**Related Issue:** Wave 93 LOC audit and cleanup
