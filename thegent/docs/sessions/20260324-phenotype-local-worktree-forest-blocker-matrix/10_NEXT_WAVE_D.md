# 10_NEXT_WAVE_D — next 24 items (6 × 4)

**Follows** `07`–`09`. **Snapshot:** 2026-03-24. No full inventory unless a dedicated inventory run. Optional **six parallel tracks** = one slice per agent when executing.

## Slice 1 — Quality gates & CI completeness (4)

1. Run repo **quality:pre-push** / equivalent; fix failures per CI completeness policy (no “pre-existing” dismissals on PRs).
2. Align **Taskfile** / `task` targets with CI jobs (names + ordering).
3. **Flaky test** registry: if any test needed retries, document in `05_KNOWN_ISSUES.md` or issue.
4. **Coverage** threshold: confirm runtime secrets/PTY suites still meet project bar after splits.

## Slice 2 — Security & supply chain (4)

5. **Dependency audit** (`bun audit` / OSV) on `heliosApp` apps touched by decomp lane.
6. **Secrets scan** (gitleaks or similar) on branch before merge.
7. **SAST** / linter on new/edited TS: no new suppressions without justification.
8. Review **credential-store** event payloads for **PII** in logs (bus topics unchanged).

## Slice 3 — Documentation & discoverability (4)

9. Update **session overview** when wave 07–10 items complete (or strike stale bullets).
10. **Link** `07`–`10` from a single `README` in the session folder if one is added later (optional).
11. **Onboarding** one-pager: “where worktrees live” + `04_QUEUE_CADENCE.md` pointer.
12. **Troubleshooting**: ENOSPC + `.tmp` + Bun cache (short subsection) in repo docs if missing.

## Slice 4 — Git delivery & PR hygiene (4)

13. **Stacked PRs**: if decomp depends on another branch, document dependency order in PR body.
14. **Rebase** feature branch on target before final review; no force-push to shared branches without policy.
15. **Resolve all review threads** before merge (org protocol).
16. **Squash vs merge** strategy per repo rules; state in PR.

## Slice 5 — Worktree governance & cleanup (4)

17. **Oldest-first** finalization: run `worktree_governance.sh oldest-first` when ready to merge lanes.
18. Remove **empty** or **broken** worktree entries after successful prune.
19. **Symlink** policy: document `*-wtrees` vs `repos/worktrees/...` migration path.
20. **Legacy** `PROJECT-wtrees`: track remaining count; reduce one folder per sprint.

## Slice 6 — Technical debt & observability (4)

21. **File size**: re-scan `wc -l` hotspots >350 in `apps/runtime` after merges; plan next split.
22. **TODO/FIXME** in touched files: zero or ticketed.
23. **Metrics/logging**: if new bus events, confirm log levels don’t leak secrets.
24. **Post-merge** smoke: one manual path (e.g. open app, run CLI) if product requires it.

---

**Roles:** **QA/CI** → slice 1; **AppSec** → slice 2; **Tech writer / onboarding** → slice 3; **EM or release captain** → slice 4; **Platform** → slice 5; **Tech lead** → slice 6.
