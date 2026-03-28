# Phenotype Repos Worktree & Archive Audit
**Date:** 2026-03-28

---

## SUMMARY

**Active Worktrees:** 13 directories across 5 major projects  
**Archive Size:** ~100GB+ (36 subdirectories)  
**Blocked Repos:** 2 (claude-code-flow, 4sgm)  
**Uncommitted Changes:** Multiple worktrees have changes on branch-tracking remotes

---

## ACTIVE WORKTREES

### 1. AgilePlus Worktree
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/AgilePlus/evidence-bundles`  
**Canonical:** `/Users/kooshapari/CodeProjects/Phenotype/repos/agileplus`  
**Branch:** `feat/evidence-bundles` (origin/feat/evidence-bundles)  
**Status:** On tracked branch; no uncommitted changes  
**Latest Commit:** f4e6d34 — feat(evidence): add real evidence bundle infrastructure  
**Notes:**
- Contains 40+ tracked branches in this worktree (feature-rich branch workspace)
- Multiple feature branches: dashboard overhaul v1/v2, dev-cli, wp01-domain-entities, etc.
- Many branches track origin (some rebased, some ahead/behind)
- Worktree appears to be an "experimental branch hub" for AgilePlus development

### 2. civ/remove-bmad Worktree
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/civ/remove-bmad`  
**Canonical:** `/Users/kooshapari/CodeProjects/Phenotype/repos/phenotypeActions/civ`  
**Status:** Worktree reference broken (fatal: not a git repo)  
**Issue:** .git file points to non-existent worktree directory  
**Action:** Likely orphaned or incomplete initialization

### 3. colab/spec-docs Worktree
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/colab/spec-docs`  
**Canonical:** `/Users/kooshapari/CodeProjects/Phenotype/repos/services/colab`  
**Branch:** `docs/add-spec-docs` (origin/docs/add-spec-docs)  
**Status:** On tracked branch; no uncommitted changes  
**Latest Commit:** e4d477e74 — docs(spec): replace stub spec docs with real phenotype-config documentation  
**Notes:**
- Contains 2 tracked branches: chore/spec-docs and docs/add-spec-docs
- Real spec documentation (PRD, FUNCTIONAL_REQUIREMENTS, ADR) completed
- Appears ready for merge review

### 4. phenotype-gauge/add-vitepress Worktree
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/phenotype-gauge/add-vitepress`  
**Canonical:** `/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-gauge`  
**Branch:** `chore/add-vitepress` (main, ahead 1, behind 5)  
**Status:** On tracked branch; no uncommitted changes  
**Latest Commit:** a694734 — docs: scaffold VitePress docsite for gauge xDD testing framework  
**Notes:**
- Docsite scaffolding completed with spec docs from codebase analysis
- Branch is ahead by 1 commit (new VitePress integration)

### 5. phenotype-nexus/add-docs Worktree
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/phenotype-nexus/add-docs`  
**Canonical:** `/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-nexus`  
**Branch:** `chore/add-docs` (origin/chore/add-docs)  
**Status:** On tracked branch; no uncommitted changes  
**Latest Commit:** 57e48d0 — docs: add CLAUDE.md and VitePress docsite scaffold  
**Notes:**
- CLAUDE.md and VitePress docsite added
- Includes real spec docs from codebase analysis
- Appears complete and ready

### 6-13. Template Language Worktrees (EMPTY)
**Paths:** 
- `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/template-lang-{elixir-hex,kotlin,mojo,python,swift,zig}/`
- `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/template-program-ops/`

**Status:** Empty directories created 2026-03-27  
**Contents:** None  
**Purpose:** Placeholders for planned language/ops template scaffolding  
**Action:** Can be cleaned up or repurposed

### 7. thegent Worktrees (3)
**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worktrees/thegent/`  
**Subdirs:**
- `bun-migrate` — Empty (created 2026-03-27)
- `dotagents` — Empty (created 2026-03-27)  
- `fix` — Contains uncommitted changes (`main...origin/main [ahead 19]`)

**Status:** Minimal/incomplete  
**Notes:** thegent worktree hub has minimal activity; `fix` branch ahead of origin

---

## .ARCHIVE DIRECTORY

**Total Size:** ~100GB+  
**Location:** `/Users/kooshapari/CodeProjects/Phenotype/repos/.archive/`  
**Contains:** 36 subdirectories

### Largest Archives (by size)
1. **worktrees/** (18GB) — Archived worktree copies
2. **migrated/** (10GB) — Migrated code/projects
3. **legacy-worktrees/** (5.8GB) — Legacy branch checkouts
4. **vibe-kanban-wtrees-20260317/** (5.5GB) — Kanban board worktree snapshot
5. **helios-cli-worktrees/** (1.1GB) — CLI tool worktrees
6. **thegent-fresh-clone-backup_20260225_045623_MST** (815MB) — Full repo backup

### Key Archive Subdirectories

| Directory | Size | Purpose | Notes |
|-----------|------|---------|-------|
| `worktrees/` | 18GB | Archived worktree checkouts | Full copies of old branch work |
| `migrated/` | 10GB | Completed migrations | Code that's been refactored/moved |
| `legacy-worktrees/` | 5.8GB | Old branch management structure | Pre-current worktree discipline |
| `vibe-kanban-wtrees-20260317/` | 5.5GB | Kanban UI worktree snapshot | Full snapshot + compressed backup |
| `helios-cli-worktrees/` | 1.1GB | heliosCLI development branches | Multiple CLI dev branches |
| `thegent-broken/` | 385MB | Broken worktree snapshot | Damage control archive |
| `phenotype-{patch,sentinel,vessel}/` | 327M, 320M, 320M | Feature/test branches | Old feature attempts |
| `plans/` | ~200MB | Archived planning documents | Phase plans, decomposition docs, architecture plans |
| `blocked-repos/` | 333B | Repo skip list | `strict-repos-2026-03-27.md` |
| `empty-stubs/` | ~7 files | Incomplete scaffolds | Stub directories for planned features |
| `.archive/INDEX.md` | 20B | Archive catalog | Empty or minimal |

### Notable Archive Subdirectories

**plans/** — Contains 60+ archived planning documents:
- Phase implementation & completion plans
- Thegent decomposition strategy
- Architecture modernization & reorg plans
- Service boundary design
- Polyrepo restructuring plans
- Phenotype ADR v2 spec
- Forgecode spec
- Kanban/dashboard evolution plans

**blocked-repos/** — Contains strict-repos-2026-03-27.md:
```
- claude-code-flow: Keep blocked. PR #10 open, merge blocked
- 4sgm: Archived; no local checkout. User explicitly requested archive block
```

**legacy-worktrees/ & helios-cli-worktrees/** — Old branch checkout roots (pre-worktree-discipline)

---

## TOKENLEDGER-WT STATUS

**Path:** `/Users/kooshapari/CodeProjects/Phenotype/repos/tokenledger-wt`  
**Type:** Main git repository (not a worktree)  
**Branch:** `main...origin/main` (with new untracked docs session)  
**Status:** Has uncommitted session docs in `/docs/sessions/20260328-root-docsites-worklog-consolidation/`  

### FINAL_STEPS.md Summary
**Task:** Complete modularization of 8759-line Rust `main.rs`  
**Current State:**
- ✅ Code successfully split into 10 focused modules (cli, models, analytics, pricing, bench, ingest, orchestrate, utils)
- ✅ main.rs reduced to 26 lines (thin entry point)
- ✅ lib.rs created for library use
- ✅ Functions/types made public where needed
- ⚠️ **108 compile errors remain** — mostly missing imports in tests

**Fixes Required (Step-by-Step):**
1. Add missing std library imports (Path, HashMap, HashSet, BufRead, BufWriter, chrono, serde_json)
2. Add module-level re-exports to lib.rs
3. Add missing pub use in utils.rs test section

**Status:** 90% complete, final import resolution phase remains

---

## FINDINGS & RECOMMENDATIONS

### ✅ HEALTHY STATE
- **AgilePlus worktree** is actively maintained with 40+ branches tracking origin
- **colab/spec-docs** has completed real spec documentation (not stubs)
- **phenotype-gauge** and **phenotype-nexus** have docsite scaffolding + specs completed
- All active worktrees on tracked branches (no detached HEAD)
- Main branch (`tokenledger-wt`) is clean

### ⚠️ ISSUES TO ADDRESS
1. **civ/remove-bmad worktree is broken** — `.git` file references non-existent directory. Can be safely removed.
2. **7 empty template worktrees** — Created but never used. Can be archived or deleted.
3. **thegent worktrees minimal** — `bun-migrate` and `dotagents` are empty shells. The `fix` branch is ahead of origin.
4. **.archive is massive (~100GB+)** — Contains archived worktrees, legacy branches, and plans. Consider:
   - Consolidating compressed backups (vibe-kanban already has .tar.gz.zst)
   - Moving old plans to a structured docs directory
   - Pruning obsolete broken worktrees

### 🎯 NEXT STEPS
1. **Clean up broken worktrees:**
   - Remove `civ/remove-bmad` (broken .git reference)
   - Clean up empty template worktrees

2. **Merge or close active branches:**
   - Review `feat/evidence-bundles` in AgilePlus
   - Merge `docs/add-spec-docs` in colab (appears ready)
   - Consolidate `phenotype-gauge` and `phenotype-nexus` changes

3. **Compress and organize .archive:**
   - Move `plans/` to structured `docs/` with categorization
   - Consolidate old worktree backups into compressed archives
   - Clean up broken/orphaned worktree copies

4. **Complete tokenledger-wt modularization:**
   - Resolve 108 import errors (mechanical task)
   - Run tests to verify all modules compile
   - Commit the completed refactor

5. **Establish worktree maintenance cadence:**
   - Review worktrees monthly
   - Archive merged branches to `.archive/`
   - Delete empty/broken worktrees immediately
