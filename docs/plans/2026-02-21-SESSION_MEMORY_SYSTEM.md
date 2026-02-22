# WL-155 Session Memory & Documentation System

## Scope
- Capture exact prompt text and agent synthesis for every run dump.
- Persist structured metadata for traceability.
- Keep output machine-readable and human-readable.

## Next-20 Execution Batch (Completed)
1. Added structured frontmatter to runtime dump files.
2. Added `prompt` field to runtime dump writer.
3. Added `synthesis` field to runtime dump writer.
4. Added `category` partitioning for dump output directories.
5. Added `tags` support for dumps.
6. Added `metadata` support for dumps.
7. Added markdown sections: Prompt, Synthesis, Full Output.
8. Ensured UTF-8 output encoding for dumps.
9. Updated dump listing to recurse category subdirectories.
10. Wired runtime run-core to pass prompt into dumps.
11. Wired runtime run-core to pass synthesis into dumps.
12. Wired runtime run-core to tag dumps with session-memory markers.
13. Wired runtime run-core to persist run metadata (exit code, timeout).
14. Added unit test for prompt/synthesis serialization.
15. Added unit test for recursive category dump discovery.
16. Added explicit session-memory category naming in runtime path.
17. Preserved backward compatibility for existing call sites (content positional arg).
18. Preserved deterministic filename format with run-id and timestamp.
19. Preserved docs-root fallback behavior from existing runtime logic.
20. Validated dump output structure through targeted unit tests.

## Files
- `src/thegent/research/always_write_dumps.py`
- `src/thegent/cli/services/run_execution_core_helpers.py`
- `tests/test_unit_always_write_dumps.py`

## Next-20 Execution Batch 2 (Completed)
1. Added runtime category routing to split execution vs error dumps.
2. Added explicit `error` dump categorization on non-zero exit.
3. Added explicit `error` dump categorization on timeout.
4. Added automatic content tag inference from hashtags.
5. Added automatic `decision` tag inference for decision lines.
6. Added automatic `fact` tag inference for fact lines.
7. Ensured inferred tags are normalized and deduplicated.
8. Kept explicit tags override behavior when provided.
9. Preserved markdown frontmatter output shape after inference.
10. Added test coverage for inferred tag behavior.
11. Wired run metadata capture for error and success paths.
12. Kept runtime dump writing fail-safe (no user-facing crash on dump failure).
13. Preserved existing list-dumps recursive behavior.
14. Ensured category directories are auto-created.
15. Preserved deterministic run-id based file naming.
16. Kept default category as `execution` for compatibility.
17. Added session-memory trigger tags to runtime dumps.
18. Preserved UTF-8 handling across inferred-tag output.
19. Maintained backward compatibility with positional content argument.
20. Validated behavior via targeted unit tests.

## Next-35 Execution Wave Addendum (Completed)
1. Added JSON companion output for conversation dumps.
2. Added metadata linking markdown to JSON companion path.
3. Added recursive JSON dump discovery helper.
4. Added dedicated batch tests for companion behavior.
5. Validated companion write/default/disable/list semantics.

## Next-35 Execution Wave 2 Addendum (Completed)
1. Added latest dump lookup helpers for markdown/JSON (`latest_dump`).
2. Added fail-open dump JSON loader (`load_dump_json`).
3. Added category summary aggregation for dumps (`summarize_dump_categories`).
4. Added dump index JSON/markdown exports (`persist_dump_index`, `export_dump_index_markdown`).
5. Added focused batch test coverage for latest/category/index helpers.

## Next-35 Execution Wave 3 Addendum (Completed)
1. Surfaced dump operations under `memory dump` CLI app (`index`, `latest`).
2. Added CLI package-level exports for snapshot/dump command handlers in `src/thegent/cli/__init__.py`.
3. Added daily export JSON-mode support in `snapshot_daily_export_cmd` and preserved rich output.
4. Normalized blank `category` in `dump_latest_cmd` for stable behavior.
5. Added focused tests for team command exports and memory app help surfaces.

## Next-35 Execution Wave 4 Addendum (Completed)
1. Added `dump_index_payload()` for non-persisting dump index computation.
2. Added `list_dump_categories()` for sorted markdown dump category discovery.
3. Refactored dump index persistence to reuse shared payload builder.
4. Enhanced dump index markdown with total markdown dump count.
5. Added focused batch-7 tests for new dump index/category payload contracts.

## Next-35 Execution Wave 5 Addendum (Completed)
1. Added `dump_categories_cmd` to team command surface.
2. Added `memory dump categories` app command with rich/json output support.
3. Added CLI package exports for `snapshot_daily_totals_cmd` and `dump_categories_cmd`.
4. Added focused tests for command exports via `thegent.cli` package surface.
5. Validated dump/snapshot command compatibility with expanded routing contracts.

## Next-35 Execution Wave 6 Addendum (Completed)
1. Added `latest_dump_by_category(json_only=...)` supporting markdown and JSON category resolution.
2. Extended dump index payload with `latest_by_category` mapping.
3. Extended dump index markdown with a `Latest By Category` section.
4. Added focused batch-8 tests for latest-by-category and markdown section coverage.
5. Preserved backward-compatible payload expectations in prior batch tests while extending fields.
