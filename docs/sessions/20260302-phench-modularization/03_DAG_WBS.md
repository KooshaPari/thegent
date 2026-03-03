# Phench Modularization and Project-Orchestration WBS

Current milestone state:
- [done] feat(thegent): add projects modules command and manifest listing (`018c148c3`)
- [done] feat(phench): expose runtime module discovery helper (`8a0cf4bbe`)
- [done] chore(phench): sync audit metadata and module source roots (`e692ba7e5`)
- [done] chore(phench): make missing module manifest schema defaults migration-compatible
- [done] feat(phench): add cross-repo shared module scan + sync helper functions in service
- [done] feat(phench): add `phench_modules` command module and base command wiring
- [done] feat(thegent): export service helpers used by CLI (`audit_shared_modules_across_repos`, `sync_project_modules_from_repos`)

## Phase 1: Foundation and Discovery [discovery]

1. [done] Phase1.01 - Confirm module boundary model and repo scan assumptions.
2. [done] Phase1.02 - Add cross-repo audit helper to enumerate shared module ownership signals.
3. [done] Phase1.03 - Add cross-repo sync helper to harvest repo-local module manifests.
4. [done] Phase1.04 - Add default repo exclusion set for shared scan and sync (`4sgm`, `trace`, `parpour`, `civ`).
5. [done] Phase1.05 - Wire helper imports/exports for top-level `thegent.phench` API.

## Phase 2: CLI Surface [commandization]

6. [done] Phase2.01 - Register `phench modules` typer namespace.
7. [done] Phase2.02 - Register `phench modules audit` command and options.
8. [done] Phase2.03 - Register `phench modules sync` command and options.
9. [done] Phase2.04 - Route `phench modules` dispatches through dedicated service adapters.
10. [done] Phase2.05 - Print JSON payloads for both new commands.
11. [done] Phase2.06 - Add command-level integration tests for dispatch paths under `tests/commands/test_apps_main.py`.
12. [done] Phase2.07 - Add CLI reference docs for `phench modules audit|sync`.

## Phase 3: Service Validation [validation]

13. [done] Phase3.01 - Add unit tests for `audit_shared_modules_across_repos` including filters/excludes.
14. [done] Phase3.02 - Add unit tests for `sync_project_modules_from_repos` dry-run mode.
15. [done] Phase3.03 - Add unit tests for `sync_project_modules_from_repos` conflict detection and overwrite behavior.
16. [done] Phase3.04 - Verify default repo exclusions are honored across both helpers.
17. [done] Phase3.05 - Confirm error paths for invalid manifests and missing JSON content.

## Phase 4: Runtime and Governance Integration [orchestration]

18. [done] Phase4.01 - Add `Phenotype/projects` destination manifest generation integration checks.
19. [done] Phase4.02 - Confirm merged module manifests are sorted and deterministic.
20. [done] Phase4.03 - Validate sync behavior under mixed include/exclude module filters.
21. [done] Phase4.04 - Validate audit output `moduleization_candidates` against existing `projects/modules`.
22. [todo] Phase4.05 - Add targeted smoke command tests in local workflow to ensure `--include/--exclude` combos.

## Phase 5: Documentation and Delivery [handoff]

23. [done] Phase5.01 - Update WBS to reflect all remaining moduleization and worktree follow-up tasks.
24. [todo] Phase5.02 - Track residual work for worktree split lanes (`thegent-app`, `thegent-mcp`, `thegent-control-plane`, `thegent-execution`, `thegent-governance`).
25. [todo] Phase5.03 - Capture remaining blockers, risks, and next-step execution plan for handoff.
26. [todo] Phase5.04 - Run quality verification and report residual findings.

## Dependencies (DAG)

- P1.01 -> P1.02 -> P1.03
- P1.02 -> P2.01
- P1.03 -> P2.02, P2.03
- P1.04 -> P2.02, P2.03, P3.04
- P1.05 -> P2.04
- P2.01 -> P2.05 -> P2.06 -> P2.07 -> P3.01
- P3.01 -> P3.02 -> P3.03
- P3.03 -> P4.01
- P1.03 -> P3.01
- P1.04 -> P3.04
- P4.05 -> P5.01
- P5.04 -> P5.03

## Status Legend

- [done] - Completed and verified in code.
- [todo] - Planned or in progress.
- [in_progress] - Actively being implemented.
- [blocked] - Waiting on external gate or dependency.

## Critical Path (Current)

1. P1.01 -> P1.02 -> P1.03 -> P2.01 -> P2.02 -> P2.03 -> P3.01 -> P3.03 -> P4.01 -> P5.01 -> P5.02 -> P5.03
