Implement: Add `thegent_dag_recover` MCP tool that wraps `dag_recover_cmd` logic.

Requirements:
1. Add `dag_recover_impl(cd, action)` in `src/thegent/cli_impl.py` - returns dict with `changed`, `action`, `error` (if any). Mirror the logic from `dag_recover_cmd` in cli.py.
2. Refactor `dag_recover_cmd` in `src/thegent/cli.py` to call `dag_recover_impl`.
3. Add `thegent_dag_recover(cd, action)` MCP tool in `src/thegent/mcp_tools_modes.py` - calls `dag_recover_impl`. action: retry-failed | clear-stuck | reset-retries | fallback.
4. Add icon for `thegent_dag_recover` in `mcp_server.py` TOOL_ICONS.
5. Run tests: `pytest tests/test_unit_cli_impl_dag.py::TestDagRecoverCmd -v`

[TIME CONSTRAINT: You have approximately 26 tool calls (~60s). When done or when approaching this limit, wrap up and report. Do not start new multi-step work.]

[OUTPUT FORMAT: End your response with a brief worker status report: **Summary** (1–2 sentences), **Items Done** (bullet list), **Issues** (if any), **Next Steps** (bullet list). Use markdown. This is the primary output shown.]
