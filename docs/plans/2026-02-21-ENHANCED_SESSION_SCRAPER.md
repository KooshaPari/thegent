# WL-156 Enhanced Session Scraper (Rich Extraction)

## Scope
- Produce rich snapshots from active sessions.
- Extract commands, files, facts, decisions, and tags in addition to prompts.
- Persist snapshots as structured JSON artifacts.

## Next-20 Execution Batch (Completed)
1. Added `SessionSnapshot` dataclass for structured snapshot payloads.
2. Added snapshot identity and timestamp fields.
3. Added trigger field support (`manual`, `periodic`, `tool_use`, etc.).
4. Added project-root provenance in snapshots.
5. Added prompt extraction normalization utility.
6. Added command extraction heuristics from pane content.
7. Added file-path extraction regex coverage.
8. Added fact extraction (`fact:` lines).
9. Added decision extraction (`decision:` lines).
10. Added hashtag tag extraction (`#tag` syntax).
11. Added source attribution list per snapshot.
12. Added order-preserving deduplication helper.
13. Updated tmux prompt scraping to use shared structured extractor.
14. Hardened Claude history scraping for multiple key shapes.
15. Kept Ante history scraping and dedup behavior stable.
16. Added rich `collect_snapshot()` API.
17. Added `persist_snapshot()` JSON writer API.
18. Added default snapshot output dir under `docs/dumps/session-snapshots/`.
19. Added unit test covering structured extraction fields.
20. Added unit test covering snapshot persistence JSON contract.

## Files
- `src/thegent/orchestration/state/session_scraper.py`
- `tests/test_unit_session_scraper.py`

## Next-20 Execution Batch 2 (Completed)
1. Wired run execution path to persist scraper snapshots.
2. Added `tool_use` trigger emission for successful run snapshots.
3. Added `error` trigger emission for failed/timed-out run snapshots.
4. Kept snapshot persistence non-fatal (debug log on failure).
5. Wired summary command flow to persist `session_change` snapshots.
6. Attached snapshot path metadata to recorded memory entries.
7. Preserved existing prompt auto-scrape behavior.
8. Preserved summary command fail-open behavior for scraper issues.
9. Ensured snapshot persistence uses resolved working directory context.
10. Kept trigger taxonomy explicit (`tool_use`, `error`, `session_change`).
11. Kept source attribution in snapshot payload for downstream indexing.
12. Preserved default snapshot destination under docs dumps.
13. Preserved ability to override output directory for tests/tools.
14. Preserved order-stable dedupe for extracted prompt sets.
15. Preserved compatibility for existing `collect_all_recent_prompts` callers.
16. Preserved lightweight extraction without additional runtime deps.
17. Integrated lifecycle wiring in core execution helper.
18. Integrated lifecycle wiring in team summary command.
19. Verified extraction + persistence tests remain green after wiring.
20. Recorded execution batch progress for WL-156.

## Next-20 Execution Batch 3 (Completed)
1. Added snapshot listing API with newest-first ordering.
2. Added listing `limit` support.
3. Added listing filter by trigger.
4. Added listing filter by tag.
5. Added resilient loading for malformed snapshot JSON.
6. Added explicit `load_snapshot()` API.
7. Added `latest_snapshot()` convenience API.
8. Added markdown renderer for structured snapshots.
9. Added markdown export helper for stored snapshots.
10. Added export default path behavior (`.json` -> `.md`).
11. Preserved optional custom export path support.
12. Preserved non-throwing list behavior on missing directories.
13. Preserved typed snapshot return objects across load/latest.
14. Added test coverage for trigger filtering.
15. Added test coverage for tag filtering.
16. Added test coverage for latest snapshot selection.
17. Added test coverage for markdown export content.
18. Kept extraction/persistence tests passing with new APIs.
19. Ensured markdown includes prompts/commands/files/facts/decisions/tags sections.
20. Recorded execution batch progress for WL-156 utilities.

## Next-20 Execution Batch 4 (Completed)
1. Added snapshot summary/index API (`summarize_snapshots`).
2. Added total snapshot count aggregation.
3. Added total prompt count aggregation.
4. Added total command count aggregation.
5. Added total file count aggregation.
6. Added trigger histogram aggregation.
7. Added tag frequency aggregation.
8. Added latest captured timestamp aggregation.
9. Added index generated timestamp field.
10. Added JSON index persistence (`persist_snapshot_index`).
11. Added markdown index renderer (`snapshot_index_markdown`).
12. Added markdown index export (`export_snapshot_index_markdown`).
13. Wired summary auto-scrape to write snapshot index JSON.
14. Wired summary auto-scrape to write snapshot index markdown.
15. Attached index paths to memory metadata records.
16. Preserved fail-open behavior in summary auto-scrape path.
17. Added unit coverage for index summary totals.
18. Added unit coverage for trigger/tag histogram correctness.
19. Added unit coverage for index JSON/markdown export.
20. Recorded execution batch progress for WL-156 indexing pipeline.

## Next-35 Execution Wave (6 Child Agents + Primary) — Completed
1. Added `since` filter support in snapshot listing API.
2. Added `prune_snapshots` API with keep-limit semantics.
3. Added `list_triggers` API for unique trigger discovery.
4. Added `list_tags` API for frequency-ranked tag discovery.
5. Enforced fail-open behavior for invalid snapshot records.
6. Added focused batch test file for scraper wave additions.
7. Added malformed-json coverage for list/prune behavior.
8. Added trigger uniqueness coverage.
9. Added tag frequency ordering coverage.
10. Added since-filter coverage.
11. Added dedicated snapshot CLI helper module.
12. Added helper payload for snapshot list output.
13. Added helper payload for snapshot index output.
14. Added helper payload for snapshot export output.
15. Added helper payload for snapshot prune output.
16. Added helper payload for trigger/tag metadata output.
17. Added focused batch test file for helper module.
18. Added helper list payload shape/count coverage.
19. Added helper index top-tags cap coverage.
20. Added helper export payload coverage.
21. Added helper prune payload coverage.
22. Added helper trigger/tag payload coverage.
23. Added JSON companion dump API for runtime dump writer.
24. Added optional `write_json_companion` toggle to markdown dump writer.
25. Added `json_companion_path` metadata propagation.
26. Added recursive JSON dump listing API.
27. Added focused batch test file for dump-writer wave additions.
28. Added companion JSON default-write coverage.
29. Added companion JSON opt-out coverage.
30. Added markdown metadata json-path coverage.
31. Added recursive JSON list coverage.
32. Added snapshot command helpers to `team_cmds` (`list/index/export/prune/meta`).
33. Integrated helper payload rendering in team command output paths.
34. Resolved prune malformed-file behavior to satisfy fail-open contract.
35. Validated combined wave with targeted regression suite (25 passing tests).

## Next-35 Execution Wave 2 (Completed)
1. Added daily snapshot aggregation API by day (`summarize_snapshots_by_day`).
2. Added daily snapshot JSON index persistence (`persist_snapshot_daily_index`).
3. Added daily snapshot markdown rendering/export (`snapshot_daily_index_markdown`, `export_snapshot_daily_index_markdown`).
4. Added CLI helper payloads for daily index/export and strengthened helper delegation/fallback behavior for list/prune paths.
5. Added focused batch test coverage for scraper daily APIs and CLI daily helper payloads.

## Next-35 Execution Wave 3 (Completed)
1. Surfaced snapshot operations under `memory snapshot` CLI app (`list/index/export/prune/meta`).
2. Surfaced daily snapshot operations under `memory snapshot` (`daily-index`, `daily-export`).
3. Added snapshot/dump command export coverage in `team_cmds.__all__` for CLI shim visibility.
4. Hardened snapshot daily helper payload compatibility with `daily` lookup + export alias keys.
5. Added focused command/help + payload compatibility test coverage for snapshot CLI surfaces.

## Next-35 Execution Wave 4 (Completed)
1. Added snapshot export JSON-mode support end-to-end from memory app -> team command.
2. Added daily export format pass-through (`rich|json`) in memory snapshot app.
3. Improved daily index rich rendering to prefer canonical `snapshots` metric with fallback.
4. Added daily helper summary totals (`total_prompts`, `total_commands`, `total_files`) and lightweight totals payload API.
5. Added focused routing/output tests for memory + team snapshot command surfaces.

## Next-35 Execution Wave 5 (Completed)
1. Added `snapshot_daily_totals_cmd` to team command surface for compact daily metrics output.
2. Added `memory snapshot daily-totals` app command with rich/json output parity.
3. Added filter-aware daily helper payload contracts (trigger/tag/since) for index/totals/export.
4. Added dedicated batch-9 tests for daily helper filter propagation and totals behavior.
5. Added command routing/export tests for new daily totals and dump categories surfaces.

## Next-35 Execution Wave 6 (Completed)
1. Added daily filter option plumbing (`trigger/tag/since`) across team commands and memory app daily commands.
2. Added helper-level filter passthrough for daily index/totals/export payload generation.
3. Added applied-filter aliases (`applied_filters`) for daily index/totals/export payloads.
4. Added focused command routing tests for daily filter options at both team and memory layers.
5. Added batch-10 helper tests for filter alias/propagation behavior.
