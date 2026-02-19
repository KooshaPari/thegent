Add unit tests for `dag_ready_impl` and `dag_run_impl` in `src/thegent/cli_impl.py`.

Requirements:
1. In `tests/test_unit_cli_impl_dag.py` (or new file), add:
   - `TestDagReadyImpl`: test `dag_ready_impl` returns ready_task_ids when DAG exists with pending tasks; returns error when cwd ambiguous or DAG missing.
   - `TestDagRunImpl`: test `dag_run_impl` dry_run returns would_run; test error when task not ready; test error when cwd ambiguous.
2. Use tmp_path, mock _resolve_cwd, _parse_dag_full, etc. as needed. Follow patterns from TestDagSyncCmd.
3. Run: `pytest tests/test_unit_cli_impl_dag.py -v -k "DagReadyImpl or DagRunImpl"`

[TIME CONSTRAINT: You have approximately 26 tool calls (~60s). When done or when approaching this limit, wrap up and report. Do not start new multi-step work.]

[OUTPUT FORMAT: End your response with a brief worker status report: **Summary** (1–2 sentences), **Items Done** (bullet list), **Issues** (if any), **Next Steps** (bullet list). Use markdown. This is the primary output shown.]
