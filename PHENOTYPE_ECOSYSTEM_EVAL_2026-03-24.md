# Phenotype Ecosystem - Breadth-First Evaluation Report
**Generated:** 2026-03-24  
**Scope:** 27 primary repositories

---

## Evaluation Summary Matrix

| Repo | Branches | Open PRs | Dirty | CI Status | Risk Level |
|------|----------|----------|-------|-----------|------------|
| **4sgm** | 15+ | 1 | Yes | FAIL (lint/format) | 🔴 HIGH |
| **agent-devops-setups** | 2 | 1 | Clean | N/A | 🟡 MED |
| **agent-wave** | 2 | 0 | Clean | N/A | 🟢 LOW |
| **agentapi-plusplus** | 20+ | 5 | Clean | PASS | 🟢 PASS |
| **agentops-policy-federation** | 7 | 0 | Yes | N/A | 🟡 MED |
| **AgilePlus** | 20+ | 2 | Yes | FAIL (Rust) | 🔴 HIGH |
| **bifrost-extensions** | 20+ | 5 | Yes | FAIL (Alert Sync) | 🔴 HIGH |
| **civ** | 15+ | 0 | Yes | N/A | 🟡 MED |
| **cliproxyapi-plusplus** | 20+ | 1 | Yes | N/A | 🟡 MED |
| **helios-cli** | 100+ | 3 | Clean | N/A | 🟡 MED |
| **heliosApp** | 20+ | 5 | Yes | IN PROG | 🟡 MED |
| **heliosCLI** | 20+ | 0 | Yes | N/A | 🟡 MED |
| **helMo** | 3 | 0 | Clean | N/A | 🟢 PASS |
| **parpour** | 15+ | 0 | Clean | N/A | 🟢 PASS |
| **phench** | 6 | 0 | Clean | N/A | 🟢 PASS |
| **phenotype-config** | 15+ | 0 | Yes | N/A | 🟡 MED |
| **phenotype-design** | 3 | 0 | Yes | N/A | 🟡 MED |
| **phenotype-go-kit** | 4 | 1 | Clean | N/A | 🟡 MED |
| **phenotype-infrakit** | 4 | 0 | Clean | N/A | 🟢 PASS |
| **phenotype-shared** | 8 | 1 | Clean | N/A | 🟡 MED |
| **phenotypeActions** | 12+ | 1 | Yes | PASS | 🟢 PASS |
| **policy-contract** | 3 | 0 | Clean | N/A | 🟢 PASS |
| **portage** | 20+ | 2 | Clean | FAIL (lockfile) | 🔴 HIGH |
| **thegent** | 30+ | 2 | Yes | FAIL (docs) | 🔴 HIGH |
| **tokenledger** | 12+ | 0 | Clean | N/A | 🟢 PASS |
| **trace** | 15+ | 0 | Clean | N/A | 🟡 MED |
| **trash-cli** | 12+ | 1 | Clean | N/A | 🟡 MED |

---

## 🔴 CRITICAL - Requires Immediate Fixes

### 1. 4sgm
- **Issue:** CI failures on `fix/stabilize` - lint and format checks failing
- **Open PRs:** 1
- **Dirty:** Yes (untracked workflow file, worktree)
- **Action:** Fix lint/format issues in `fix/stabilize` branch

### 2. AgilePlus  
- **Issue:** Rust compilation errors across workspace
- **Open PRs:** 2 (fix/rust-compile-errors, fix/stabilize)
- **Dirty:** Yes (Cargo.toml changes, new claude commands)
- **Action:** Resolve Rust compilation errors

### 3. bifrost-extensions
- **Issue:** Alert Sync To Issues workflow failing repeatedly
- **Open PRs:** 5
- **Dirty:** Yes (go.mod modified, docs/package-lock.json)
- **Action:** Fix Alert Sync workflow

### 4. portage
- **Issue:** Lockfile security guard failures on `chore/dotagents-setup`
- **Open PRs:** 2
- **Dirty:** Clean
- **Action:** Fix lockfile issues in dotagents-setup

### 5. thegent
- **Issue:** Docs build failures on main branch
- **Open PRs:** 2
- **Dirty:** Yes (worktrees/ directory)
- **Action:** Fix docs build

---

## 🟡 MEDIUM - Needs Attention

### Repos with Dirty Working Directories
| Repo | Issue |
|------|-------|
| agentops-policy-federation | Multiple modified files (policy, headless_review) |
| heliosApp | Runtime protocol/recovery changes staged |
| heliosCLI | .gitignore, tooling script modified |
| phenotype-config | Many staged spec-kitty command files |
| phenotype-design | CSS, VitePress config, new docs |
| thegent | Worktrees directory untracked |

### Repos with Multiple Open PRs
| Repo | Count | Notes |
|------|-------|-------|
| agentapi-plusplus | 5 | 2x docs stabilization, codex tasks |
| bifrost-extensions | 5 | oxc migration, standalone packages |
| heliosApp | 5 | oxc migration, debt parity |
| 4sgm | 1 | Stabilize branch |
| AgilePlus | 2 | Rust fixes |
| thegent | 2 | Backend splits |
| portage | 2 | Dotagents, upstream reconcile |

---

## 🟢 HEALTHY - Pass Criteria

| Repo | Status |
|------|--------|
| helMo | Clean, no PRs |
| parpour | Clean, no PRs |
| phench | Clean, no PRs |
| phenotype-infrakit | Clean, no PRs |
| policy-contract | Clean, no PRs |
| tokenledger | Clean, no PRs |
| phenotypeActions | CI passing |
| agentapi-plusplus | CI passing |
| helios-cli | Clean, stable |

---

## Breadth-First Action Plan (BFS)

### Wave 1: Critical Fixes (Parallel)
1. **4sgm** - Fix lint/format failures → Create PR
2. **AgilePlus** - Resolve Rust compilation → Create PR  
3. **bifrost-extensions** - Fix Alert Sync workflow → Create PR
4. **portage** - Fix lockfile issues → Create PR
5. **thegent** - Fix docs build → Create PR

### Wave 2: Dirty State Resolution (After Wave 1 Merges)
1. **agentops-policy-federation** - Stage/commit headless_review changes
2. **heliosApp** - Review runtime changes, decide on PR or revert
3. **heliosCLI** - Review .gitignore/tooling changes
4. **phenotype-config** - Commit spec-kitty commands or discard
5. **phenotype-design** - Merge docs improvements

### Wave 3: PR Consolidation (After Wave 2)
1. Review and merge all remaining open PRs by priority
2. Archive stale branches
3. Sync main branches

---

## Metrics Summary
- **Total Repos:** 27
- **Critical (Red):** 5 (18.5%)
- **Medium (Yellow):** 14 (51.9%)
- **Healthy (Green):** 9 (33.3%)
- **Total Open PRs:** 23
- **CI Failures:** 5 repos
- **Dirty Working Dirs:** 10 repos

---

*Report generated by breadth-first ecosystem evaluation*
