Implement: When `dag sync --watch` is used, automatically pass `auto_run_next=True` to `dag_sync_cmd` so the watch loop auto-spawns next ready DAG tasks after each sync.

Requirements:
1. In `src/thegent/main.py`, in the `dag_sync` function: when `watch=True`, pass `auto_run_next=True` to `dag_sync_cmd` (so each sync cycle also spawns next ready tasks).
2. Optionally: add a flag `--no-auto-run-next` to disable this when watch is used, so users can opt out.
3. Run existing tests to verify: `pytest tests/test_unit_main_commands.py -k "dag_sync" -v`

[TIME CONSTRAINT: You have approximately 26 tool calls (~60s). When done or when approaching this limit, wrap up and report. Do not start new multi-step work.]

[OUTPUT FORMAT: End your response with a brief worker status report: **Summary** (1–2 sentences), **Items Done** (bullet list), **Issues** (if any), **Next Steps** (bullet list). Use markdown. This is the primary output shown.]
