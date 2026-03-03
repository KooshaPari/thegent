# Thegent Phench Module Composition Wave 2

## Status Legend

- `[todo]` not started
- `[in_progress]` actively executing
- `[done]` implemented and verified
- `[blocked]` blocked with dependency

## Phased WBS + DAG

| Phase | Lane | Task ID | [status] | Description | Depends On |
|---|---|---|---|---|---|
| Discovery | A | P1 | [done] | Review existing `packages/thegent-bench` phench service model, path, and CLI surfaces to confirm extension points. | none |
| Discovery | A | P2 | [done] | Audit existing `Phenotype/projects/modules/*/manifest.json` schema and identify gaps (`default_ref` absent in some files). | P1 |
| Discovery | A | P3 | [done] | Create manifest contract for `repo_patterns`, `repo_ref_overrides`, `repo_runner_overrides`, `repo_command_overrides`, `repo_env_profile_overrides`, `default_ref`. | P2 |
| Discovery | A | [done] | P4 | Add module metadata fields to lock model (`selected_runner`, `selected_command`, `selected_env_profile`, `module_name`) and loader compatibility checks. | P3 |
| Discovery | A | P5 | [done] | Validate repo discovery baseline from `THGENT_PHENOTYPE_ROOT/repos` and default exclusion set `{4sgm,parpour,civ,trace}`. | P4 |
| Discovery | A | P6 | [done] | Add repository selection helper tests for manifest-driven path matching. | P5 |
| Build | B | P7 | [done] | Implement service-level module manifest loader and selection helper in `phench/service.py`. | P3 |
| Build | B | P8 | [done] | Implement `add_module_to_target` command path in service, including override application and deterministic lock refresh. | P7 |
| Build | B | P9 | [done] | Wire module override fields into run-time selection path (`run_target`) with per-repo env profile precedence. | P8 |
| Build | B | P10 | [done] | Add module manifest fallback behavior (`HEAD`) with explicit ref override (`--ref`) and explicit exclude set. | P8 |
| Build | B | P11 | [done] | Add and expose new API in `thegent_bench.phench.__init__`. | P9 |
| Build | B | P12 | [done] | Add `target add-module` CLI command in both `src/thegent/cli` and `packages/thegent-cli` surfaces. | P11 |
| Validate | C | P13 | [done] | Add runtime tests for module add-to-target, exclude, and per-repo runner/command/env override behavior. | P10 |
| Validate | C | P14 | [done] | Add negative tests for missing manifest and empty module selection failure. | P13 |
| Validate | C | P15 | [done] | Validate new command path through `thegent phench` CLI tests or smoke CLI script. | P12, P13 |
| Validate | C | P16 | [done] | Add manifest-specific fixture test demonstrating cross-repo load from `Phenotype/repos` candidates. | P13 |
| Validate | C | P17 | [done] | Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src:packages/thegent-bench/src:packages/thegent-cli/src python -m pytest tests/test_phench_runtime.py -q` and collect pass/fail summary. | P15 |
| Validate | C | P18 | [done] | Run `python cli.py lint check` on touched modules and resolve lint/type errors. | P17 |
| Deploy | D | P19 | [in_progress] | Merge current branch state into mainline path and verify lockfile-free doc updates are scoped under `docs/`. | P18 |
| Deploy | D | P20 | [done] | Update `Phenotype/projects/README.md` with module-add workflow and example invocations. | P19 |
| Deploy | D | P21 | [done] | Provide migration notes for `--all-repos` safety and module override fallback semantics. | P20 |
| Deploy | D | P22 | [done] | Add changelog or completion note for module composition wave execution status. | P21 |
| Deploy | D | P23 | [done] | Document extension points for `thegent-execution` and `thegent-control-plane` module patterns. | P22 |
| Deploy | D | P24 | [done] | Finalize module manifest guidance: expected schema, override precedence, and excluded repository policy. | P23 |

## Next 24-Task Wave: Shared-Module Discovery and Moduleization Rollout

| Phase | Lane | Task ID | [status] | Description | Depends On |
|---|---|---|---|---|---|
| Discovery | S1 | P25 | [done] | Add repo root selector CLI flag for `scan-shared-repos` to target sibling worktrees. | P20 |
| Discovery | S1 | P26 | [done] | Add exclusion validation for malformed repo IDs and whitespace-only values. | P25 |
| Discovery | S1 | P27 | [done] | Add `scan-shared-repos` output schema contract in JSON and docs/guide. | P26 |
| Discovery | S1 | P28 | [done] | Document candidate manifest output and `--candidates` field semantics. | P27 |
| Design | S2 | P29 | [todo] | Add helper to generate module manifest files from `scan-shared-repos` output. | P25 |
| Design | S2 | P30 | [todo] | Define manifest naming convention for detected shared modules (prefix and bounded scope). | P29 |
| Design | S2 | P31 | [todo] | Add conflict strategy for overlapping candidate modules across domains. | P30 |
| Design | S2 | P32 | [todo] | Publish moduleization rollout ADR for shared module adoption criteria. | P31 |
| Build | S3 | P33 | [todo] | Add idempotent manifest writer utility for generated module candidates. | P30 |
| Build | S3 | P34 | [todo] | Add CLI command to materialize a candidate manifest for a single module. | P33 |
| Build | S3 | P35 | [todo] | Add dry-run flag for candidate manifest generation to avoid workspace writes. | P34 |
| Build | S3 | P36 | [todo] | Add per-module repo pinning for candidate manifests (`--repos`) and min-repo count override (`--min-count`). | P35 |
| Build | S4 | P37 | [todo] | Add optional `--output-dir` for persisted manifests and index updates. | P33 |
| Build | S4 | P38 | [todo] | Add command to print shell snippets for launching module composition targets. | P37 |
| Build | S4 | P39 | [todo] | Add module recommendation output in `scan-shared-repos` sorted by repo overlap. | P36 |
| Build | S4 | P40 | [todo] | Add explicit `--all-repos` safety dry-run warnings in module composition docs. | P39 |
| Validate | S5 | P41 | [todo] | Add unit test: excluded repos are omitted even when explicit flags match manifest patterns. | P33 |
| Validate | S5 | P42 | [todo] | Add unit test: `min_repo_count` filters module report deterministically. | P41 |
| Validate | S5 | P43 | [todo] | Add unit test: candidate generation writes valid module JSON with sorted `repo_patterns`. | P40 |
| Validate | S5 | P44 | [todo] | Add CLI test for `scan-shared-repos --candidates` schema and sort order. | P43 |
| Deploy | S6 | P45 | [todo] | Update `Phenotype/projects/README.md` with `scan-shared-repos` usage examples. | P44 |
| Deploy | S6 | P46 | [todo] | Add quick-runbook for generating module set for `thegent-execution` and `thegent-control-plane`. | P45 |
| Deploy | S6 | P47 | [todo] | Extend tracker docs for moduleization candidates and ADR alignment. | P46 |
| Deploy | S6 | P48 | [todo] | Run full test sweep + lint gates and package evidence bundle for module discovery wave. | P47 |

## DAG Notes

- B lanes depend strictly on manifest contract readiness (A1–A6).
- Runtime behavior verification (P9/P10) must complete before all docs and CLI smoke targets.
- Validate/Deploy is intentionally serialized because docs and CI evidence are required before handoff.

## P19-P24 Notes

- P19: merge into mainline remains blocked by branch governance policy and should be executed through the prescribed integration branch flow when orchestration lane opens.
- P20-P24: completed in this wave with repository-local docs and operational guidance updates in this same changeset.
