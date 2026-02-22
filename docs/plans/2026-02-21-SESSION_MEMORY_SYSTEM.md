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
