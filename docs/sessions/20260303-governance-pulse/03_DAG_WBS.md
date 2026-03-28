# [done] Governance Policy & Binary Hygiene Rollout WBS

## 1) Scope
- Scope roots: `/Users/kooshapari/CodeProjects/Phenotype/repos`
- Scope scripts:
  - `/Users/kooshapari/scripts/repo-governance/sync-repo-policies.sh`
  - `/Users/kooshapari/scripts/repo-governance/check-repo-policies.sh`
  - `/Users/kooshapari/scripts/repo-governance/check-thegent-bins.sh`
  - `/Users/kooshapari/scripts/repo-governance/run-governance-audit.sh`
  - `/Users/kooshapari/restore-thegent-bins.sh`
  - `/Users/kooshapari/scripts/repo-governance/schedule-governance-audit.sh`

## 2) Phased DAG
- [done] `P1.D1` Create/normalize repo governance scripts (`--force` sync, checks, audit aggregator).
  - Depends on: none
- [done] `P1.D2` Ensure portability and determinism of checks (path canonicalization, diff strategy).
  - Depends on: `P1.D1`
- [done] `P1.D3` Execute policy sync across all repo roots.
  - Depends on: `P1.D2`
- [done] `P1.D4` Verify AGENTS/CLAUDE presence and heading counts are healthy.
  - Depends on: `P1.D3`
- [done] `P2.D1` Wire governance audit into restore workflow for post-install validation.
  - Depends on: `P1.D3`
- [done] `P2.D2` Run audit and confirm clean pass.
  - Depends on: `P2.D1`, `P1.D4`
- [done] `P3.D1` Add optional periodic scheduler helper (cron + launchd modes).
  - Depends on: `P2.D2`
- [done] `P3.D2` Publish WBS and execution artifact for handoff continuity.
  - Depends on: `P3.D1`
- [done] `P4.D1` Remove stale `scripts/tool-migrate.sh` and complete shim-path consolidation to real binaries.
  - Depends on: `P3.D2`
- [done] `P4.D2` Update shim installer/checker to harden Rust-binary linkage (`thegent-grep`, `thegent-find`, `thegent-agent`).
  - Depends on: `P4.D1`
- [done] `P4.D3` Add CI/worktree scheduled invocation for this audit.
  - Depends on: `P4.D2`
- [done] `P4.D4` Formalize operational runbook and on-call rotation cadence.
  - Depends on: `P4.D3`

## 3) Execution Matrix
| Phase | Task ID | Status | Exit criteria |
|---|---|---|---|
| Discovery | P1.D1 | [done] | All governance scripts authored and executable |
| Discovery | P1.D2 | [done] | Hash/path portability fixed; scripts are reproducible |
| Remediate | P1.D3 | [done] | 38/38 repos pass check for required section headings |
| Validate | P1.D4 | [done] | `check-repo-policies.sh` reports zero issues |
| Build | P2.D1 | [done] | `restore-thegent-bins.sh` runs audit after install |
| Validate | P2.D2 | [done] | `run-governance-audit.sh` exits 0 with pass statuses |
| Deploy | P3.D1 | [done] | `schedule-governance-audit.sh` exists and prints install options |
| Handoff | P3.D2 | [done] | Session WBS file created with dependencies and statuses |
| Remediate | P4.D1 | [done] | Stale migration shim deleted and no direct wrapper references remain |
| Remediate | P4.D2 | [done] | Install/check paths enforce real binaries for optional command families when available |
| Handoff | P4.D3 | [done] | Scheduler supports installable periodic execution (cron + launchd, configurable roots/options) |
| Handoff | P4.D4 | [done] | Runbook and audit cadence formalized across templates |

## 4) Current open blockers
- [none] all local remediation and validation tasks completed.

## 5) Suggested next sequence
1. [done] schedule periodic execution in launchd/crontab and document cadence.
2. [done] publish a short runbook pointing to `schedule-governance-audit.sh`.
