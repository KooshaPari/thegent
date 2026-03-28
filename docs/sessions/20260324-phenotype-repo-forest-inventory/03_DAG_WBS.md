# Dependency Graph and Work Breakdown Structure

## Critical path

1. Normalize the dirty/high-churn repos first.
2. Separate intentional branch work from accidental generated-file churn.
3. Reconcile branch-ahead repos with their upstreams only after pointer/state checks.
4. Validate any canonical docs or governance files that were introduced.
5. Run the repo-specific validation path after each dirty repo is classified.

## Lane 1

1. `heliosApp`: confirm `worktrees/heliosApp/dotagents` is intentional pointer drift.
2. `heliosApp`: reconcile the `ahead 8` branch with `upstream/main`.
3. `heliosCLI`: confirm `worktrees/heliosCLI/dotagents` is intentional pointer drift.
4. `heliosCLI`: reconcile the `ahead 1` branch with `origin/main`.
5. `phenotypeActions`: decide whether `.github/CODEOWNERS` is canonical policy.
6. `phenotypeActions`: validate ownership routing if `CODEOWNERS` stays.

## Lane 2

7. `phenotype-config`: confirm whether any live `spec-kitty.*` artifacts still exist.
8. `phenotype-config`: if recreated, prune duplicates and keep one canonical source per command.
9. `phenotype-config`: run the repo-specific validation path only if the artifacts reappear.
10. `phenotype-design`: classify the VitePress theme/config edits.
11. `phenotype-design`: decide the fate of added docs and policy files.
12. `phenotype-design`: run the docs/theme build after normalization.

## Lane 3

13. `AgilePlus`: review the new `agileplus.*` scaffolding.
14. `AgilePlus`: validate the API route edits.
15. `AgilePlus`: run the branch-specific test/build path.
16. `phenodocs`: treat the `.vitepress/.temp` deletions as cache cleanup or restore them.
17. `phenodocs`: run the docs build and make the cache rule explicit.
18. `thegent`: separate intentional session-doc edits from accidental churn.

## Lane 4

19. `thegent`: verify whether `.env` and `maif_private.pem` deletions are intended.
20. `thegent`: validate the CI/docs updates after the secret/file decision.
21. `trash-cli`: decide whether `.github/workflows/security-scan-schedule.yml` belongs.
22. `trash-cli`: validate or remove the scheduled workflow.
23. `agent-devops-setups`: review the `ahead 6` rollout branch.
24. `phenotype-shared`: inspect `feat/create-state-machine-crate` for merge readiness.

## Dependency notes

- The lane items are intentionally ordered by likely impact and branch risk.
- Generated-file cleanup should be resolved before merge/rebase decisions.
- Canonical docs and governance files should be separated from accidental churn before any broad validation.

## Expanded Turn Queue

25. `heliosApp`: inspect `apps/runtime/src/audit/sink.ts` for the clone/refactor delta and decide whether any further cleanup is needed.
26. `heliosApp`: validate `apps/runtime/src/index.ts` against the current branch intent.
27. `heliosApp`: validate `apps/runtime/src/protocol/validator.ts` against the current branch intent.
28. `heliosCLI`: inspect the pointer-only `worktrees/heliosCLI/dotagents` change for commit intent.
29. `heliosCLI`: decide whether the branch needs a restack or a merge from `origin/main`.
30. `heliosCLI`: record any branch-specific validation needed before merge.
31. `phenotypeActions`: inspect the repo for any untracked governance files beyond `CODEOWNERS`.
32. `phenotypeActions`: decide whether the branch should stay ahead-only or get a merge candidate prepared.
33. `phenotype-config`: treat the `spec-kitty.*` command scaffolding as a stale inventory note unless
    it is recreated.
34. `phenotype-config`: if the scaffolding returns, identify whether it should be deduplicated into
    one shared template source.
35. `phenotype-config`: if the files return, map them to their intended command surfaces.
36. `phenotype-config`: decide whether the branch needs a validation run only after live artifacts reappear.
37. `phenotype-design`: inspect the new `docs/sessions/index.md` addition for canonical placement.
38. `phenotype-design`: decide whether `package.json` name/version changes are intended release metadata or accidental renaming.
39. `phenotype-design`: determine whether the VitePress aliasing to `phenodocs` should be retained as-is.
40. `phenotype-design`: confirm whether the new `.github` files are part of a broader repository bootstrap.
41. `AgilePlus`: inspect whether the generated command scaffolding overlaps with existing command contracts.
42. `AgilePlus`: decide whether the route refactor in `crates/agileplus-api/src/state.rs` needs a follow-up test.
43. `AgilePlus`: verify whether the adapter derive removals in `crates/agileplus-git` and `crates/agileplus-sqlite` are sufficient.
44. `AgilePlus`: record merge-readiness after the successful cargo check.
45. `phenodocs`: decide whether `worktrees/phenodocs/dotagents` should be committed or left as metadata.
46. `phenodocs`: determine whether the current branch should be cleaned or rebased before further docs work.
47. `thegent`: inspect the `worktrees/thegent/dotagents/` untracked directory and decide whether it is expected metadata.
48. `thegent`: classify the broad ahead-only branch as either intentional WIP or merge debt.
49. `trash-cli`: decide whether the scheduled security scan workflow should be promoted or deleted.
50. `agent-devops-setups`: verify whether the ahead-by-6 rollout branch needs a sync with its remote.
