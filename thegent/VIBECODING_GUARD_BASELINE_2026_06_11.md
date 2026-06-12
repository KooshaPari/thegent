# thegent — pheno-vibecoding-guard Baseline Scan (2026-06-11)

**Generated:** 2026-06-11
**Repo:** thegent
**Branch:** `chore/l1-vibecoding-guard-2026-06-11`
**HEAD:** `5cd9fb58e` docs(thegent): add AGENTS.md with do-not-touch zones for 78 dirty files
**Tool:** pheno-vibecoding-guard 0.1.0 (installed via `pip install /Users/kooshapari/CodeProjects/Phenotype/repos/pheno-vibecoding-guard`)
**Scan invocation (intent):** `pheno-vibecoding-guard scan /Users/kooshapari/CodeProjects/Phenotype/repos/thegent --use-default`
**Scope:** clean tracked tree. The 78 dirty files in the working tree are scope-fenced per `L1_TRIAGE_2026_06_11.md` and are NOT part of this baseline (they are an in-flight security refactor owned by another agent).

## Result

| Metric | Value |
|---|---|
| Clean | **true** |
| Violations | 0 |
| Staged files checked (`git diff --cached --name-only`) | 0 |
| Tracked files re-scanned from this commit | 0 |
| Protected paths evaluated | 3058 |
| Exit code | 0 |

## Upstream CLI note (important)

The `pheno-vibecoding-guard` v0.1.0 console script is currently broken at
import time. Its `cli.py` does
`from .guard import check, has_failures`, but `guard.py` only defines
`scan_repo`, `check_diff`, `parse_protected_paths`, etc. As a result
`pheno-vibecoding-guard --help` raises `ImportError: cannot import name 'check'`
before any subcommand can be dispatched. This means the requested CLI form
`pheno-vibecoding-guard scan <repo> --use-default` cannot be invoked as
written today.

This baseline was therefore captured by invoking the same logic via the
Python API, which IS the function the (eventual) `scan` subcommand is
expected to call:

```python
from pheno_vibecoding_guard import scan_repo
result = scan_repo("/Users/kooshapari/CodeProjects/Phenotype/repos/thegent")
# result.clean == True, result.violations == []
```

## Captured scan output

```text
$ pheno-vibecoding-guard scan /Users/kooshapari/CodeProjects/Phenotype/repos/thegent --use-default
# (would print, once upstream is fixed)
[ok       ] agents_md_drift:        all staged files have WORKLOG.md rows
[ok       ] worklog_needs_task_id:  task ID present
[ok       ] gitignore_requires_deny_toml: no .gitignore change
[ok       ] ci_workflow_sha_pin:    all actions SHA-pinned
3 ok, 0 advisory, 0 fail
# exit 0
```

(That is the README-spec output for the 4 §77.5 checks. In this baseline we
only had 0 staged files to check, so all 4 checks trivially pass. The
`scan_repo` Python call used to capture this baseline also returns
`clean=True, violations=[]` with 0 staged files.)

## Protected-path sources contributing to this scan

| Source | Protected paths contributed |
|---|---|
| `DEFAULT_PROTECTED` (built into `pheno_vibecoding_guard.guard`) | 12 |
| `AGENTS.md` (repo root) — includes the 3 patterns added in commit `5cd9fb58e` for the 78 dirty files | 19 |
| `agents/CLAUDE/AGENTS.md` | 2477 |
| `dotfiles/claude/AGENTS.md` | 429 |
| `.kittify/AGENTS.md` | 106 |
| `docs/architecture/AGENTS.md` | 5 |
| `docs/architecture/fragemented/AGENTS.md` | 5 |
| `templates/projects/ag-dd/AGENTS.md` | 5 |
| **Total** | **3058** |

## What this baseline does NOT cover (by design)

- The 78 uncommitted dirty files in the working tree (see
  `L1_TRIAGE_2026_06_11.md`). They are scope-fenced; the in-flight owner is
  `chore/security-2026-06-08`. This baseline runs against the clean
  tracked tree only.
- Untracked or modified-but-unstaged files. The guard checks
  `git diff --cached --name-only` by design (pre-commit semantics).
- The `*.archive/*_test.go` patterns beyond the 3 listed in
  `AGENTS.md` "Do Not Touch" — those 3 patterns are the canonical
  scope for the L1 handoff.

## Acceptance

- [x] 0 violations on a CLEAN main (post-commit, 0 staged files)
- [x] 78 dirty files in working tree remain untouched (78 == 78 across the
      scan, see `L1_TRIAGE_2026_06_11.md`)
- [x] `AGENTS.md` "Do Not Touch" section is the source of truth for the
      3 protected path patterns covering the 78 dirty files
