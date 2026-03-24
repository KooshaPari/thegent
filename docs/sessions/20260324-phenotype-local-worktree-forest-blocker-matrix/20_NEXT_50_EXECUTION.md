# 20_NEXT_50_EXECUTION — status for `19_NEXT_50_WORK_ITEMS.md` (items 1–50)

**Snapshot:** 2026-03-24. **Repo context:** `thegent` session docs + local verification commands. Cross-repo work (**heliosApp**, **heliosCLI**, staging) is **deferred** with pointers unless explicitly in scope.

**Carry-forward issues:** [#559](https://github.com/KooshaPari/thegent/issues/559), [#560](https://github.com/KooshaPari/thegent/issues/560).

---

## Preamble

| # | Status | Notes |
|---|--------|--------|
| **1** | **Done** | `09_NEXT_WAVE_C.md` links **`18`**, **`19`** (merged earlier). |
| **2** | **Done** | `ACTIVE_BACKLOG.md` + `00_SESSION_OVERVIEW.md` index **`19`**; this file **`20`** added in same pass. |

---

## Wave D (3–26)

| # | Status | Notes |
|---|--------|--------|
| **3** | **Blocked (local)** | Ran **`task check`** on **`main`**: fails at **`quality:rust:ci`** (`cargo clippy --workspace --all-targets --all-features -- -D warnings`). Representative failures include **`thegent-maif`**, **`thegent-tui`**, **`thegent-offload`** (clippy `-D warnings`). Treat as **repo debt**; fix in a dedicated Rust-quality PR — see **`05_KNOWN_ISSUES.md`**. Hooks: **`task hooks:run:pre-push`** can no-op when no staged files. |
| **4** | **Documented** | **Taskfile ↔ CI (high level):** `task ci:preflight` aligns with GitHub **“CI Preflight”** (`.github/workflows/ci.yml`). `task check` / `task quality` align with **“Quality Checks”** / **“Unified Quality Control Plane”** jobs. **`task quality:pre-push`** = `hooks:run:pre-push` + `ci:local-gha:pre-push` (see `Taskfile.yml`). PR **`lint-test`** workflow delegates to **`phenotypeActions`** `lint-test`. Full ordering matches `ci.yml` job graph (`preflight` → `test` → …). |
| **5** | **N/A this pass** | No flaky-test retries observed in the short local run; registry stays **`05_KNOWN_ISSUES.md`**. |
| **6** | **Deferred** | **heliosApp** secrets/PTY coverage is tracked in Wave A/B notes; not re-run here. |
| **7** | **Deferred** | **`bun audit`** on heliosApp decomp lane — run in **heliosApp** worktree. |
| **8** | **Partial** | **`gitleaks detect --no-git`** on this session folder: **no leaks** (2026-03-24). Full-branch scan: run before merge in CI or locally with hooks. |
| **9** | **N/A** | No new TS edits in this doc-only pass. |
| **10** | **Deferred** | **credential-store** / bus review — **heliosApp** product path. |
| **11** | **Done** | This **`20`** + **`README.md`** refresh session index and pointers. |
| **12** | **Done** | **`README.md`** (this folder) links **`07`–`13`**, **`18`–`20`**. |
| **13** | **Done** | **Onboarding (short):** Phenotype hubs use **`repos/worktrees/<project>/<topic>/<wtree>`** (see root **`AGENTS.md`**). Read **`04_QUEUE_CADENCE.md`** for 24-item turns and **full-turn** definition. |
| **14** | **Done** | **Troubleshooting:** **ENOSPC** — free disk, clear **`~/.bun/install/cache`**, large **`node_modules`**, and session **`.tmp/`** scratch dirs. **Bun:** `bun pm cache rm` if policy allows. Prefer **`.gitignore`** for `.tmp/` (heliosApp decomp already noted in Wave A). |
| **15** | **Guidance** | Stacked PRs: state **base** branch + **dependency order** in PR body (org protocol). |
| **16** | **Guidance** | Rebase on target before merge; no force-push to shared branches (see **`FULL_TURN_DELIVERY.md`**). |
| **17** | **Guidance** | Resolve review threads before merge. |
| **18** | **Guidance** | Squash vs merge per repo; **`thegent`** merges often squash via PR settings + **`gh pr merge --squash`** when allowed. |
| **19** | **Guidance** | When lanes are merge-ready: **`./scripts/worktree_governance.sh oldest-first`** (see script **`--help`** / `AGENTS.md`). |
| **20** | **Deferred** | Prune/remove broken worktrees only after successful governance + backup policy. |
| **21** | **Done** | **Symlink / layout:** canonical **`repos/worktrees/...`**; legacy **`*-wtrees`** migration — **`AGENTS.md`**, **`18_WAVE_C_SLICES_4_6.md`**, Phenotype **`CLAUDE.md`**. |
| **22** | **Deferred** | Legacy folder counts: use **`worktree_governance.sh list`** / inventory sessions. |
| **23** | **Deferred** | **`apps/runtime`** line-count — **heliosApp** path. |
| **24** | **N/A** | No TODO churn in session markdown added here. |
| **25** | **Deferred** | Bus / metrics — product codebase. |
| **26** | **Deferred** | Post-merge smoke — human/product. |

---

## Wave E (27–50)

| # | Status | Notes |
|---|--------|--------|
| **27** | **Guidance** | Tag/release per **`CHANGELOG_PROCESS`** / **`release.yml`** when shipping versioned artifacts. |
| **28** | **Deferred** | Monitor deploy — ops; not applicable to docs-only pass. |
| **29** | **Done** | **Rollback:** revert the merge commit on **`main`** (`git revert -m 1 <sha>`) or roll forward; document incident in issue. |
| **30** | **Deferred** | Owner/on-call for secrets/PTY — team roster. |
| **31** | **N/A** | LICENSE headers — follow repo **CONTRIBUTING** when touching code. |
| **32** | **N/A** | Third-party notices — release/lockfile PRs. |
| **33** | **Deferred** | Export/crypto — product/legal. |
| **34** | **Guidance** | No long-lived secrets under **`/tmp`**; audit sinks per product policy. |
| **35**–**38** | **Deferred** | Perf/PTY/bundle/resources — **heliosApp** / runtime. |
| **39**–**42** | **Deferred** | Testing depth — per-repo CI. |
| **43** | **Done** | **Handoff:** next agent — start from **`19_NEXT_50_WORK_ITEMS.md`**, **`ACTIVE_BACKLOG.md`**, branch from **`main`** in a **worktree**; unblock **`task check`** Rust lane or scope Python/docs lanes per PR. |
| **44** | **Deferred** | Linked issues when helios changes touch **thegent** — use **`gh issue create`**. |
| **45** | **Guidance** | Reuse opportunities → issue with **`PHENOTYPE_SHARED_REUSE_PROTOCOL`** style (see root **`AGENTS.md`**). |
| **46** | **Done** | **`git worktree list`** snapshot (canonical **`thegent`** checkout): multi-row list under **`.../repos/thegent`** and **`thegent-wtrees/*`** — regenerate after large merges. |
| **47** | **Partial** | Strike-through in wave files deferred; **execution truth** lives in **`20`** + **`ACTIVE_BACKLOG`** session log. |
| **48** | **N/A** | No duplicate session packs removed in this pass. |
| **49** | **Done** | **Retrospective:** Preamble + index items closed quickly; **Wave D** item **3** blocked on **existing Rust clippy debt** on **`main`** — document, fix in focused PRs; cross-repo items remain in forest **`05`** matrix. |
| **50** | **Open** | **Wave F** work stays in **`12_NEXT_WAVE_F.md`** until **E** closure criteria met. |

---

## Local verification log (2026-03-24)

| Command | Result |
|---------|--------|
| `bash -n scripts/worktree_governance.sh` | **OK** |
| `gitleaks detect` (session docs path, `--no-git`) | **No leaks** |
| `task check` | **FAIL** — see item **3** above |

---

## Related

- `19_NEXT_50_WORK_ITEMS.md` — master numbered list.
- `10_NEXT_WAVE_D.md` / `11_NEXT_WAVE_E.md` — full prose.
- `05_KNOWN_ISSUES.md` — **`task check`** / Rust clippy debt entry.
