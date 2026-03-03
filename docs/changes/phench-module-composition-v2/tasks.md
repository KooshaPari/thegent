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
| Validate | C | P17 | [blocked] | Run `python cli.py test run` targeted to `tests/test_phench_runtime.py` and collect pass/fail summary. | P15 |
| Validate | C | P18 | [done] | Run `python cli.py lint check` on touched modules and resolve lint/type errors. | P17 |
| Deploy | D | P19 | [todo] | Merge current branch state into mainline path and verify lockfile-free doc updates are scoped under `docs/`. | P18 |
| Deploy | D | P20 | [todo] | Update `Phenotype/projects/README.md` with module-add workflow and example invocations. | P19 |
| Deploy | D | P21 | [todo] | Provide migration notes for `--all-repos` safety and module override fallback semantics. | P20 |
| Deploy | D | P22 | [todo] | Add changelog or completion note for module composition wave execution status. | P21 |
| Deploy | D | P23 | [todo] | Document extension points for `thegent-execution` and `thegent-control-plane` module patterns. | P22 |
| Deploy | D | P24 | [todo] | Finalize module manifest guidance: expected schema, override precedence, and excluded repository policy. | P23 |

## DAG Notes

- B lanes depend strictly on manifest contract readiness (A1–A6).
- Runtime behavior verification (P9/P10) must complete before all docs and CLI smoke targets.
- Validate/Deploy is intentionally serialized because docs and CI evidence are required before handoff.
