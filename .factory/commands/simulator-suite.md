---
description: Guide droid through running the MCP simulator tests
argument-hint: <scope-or-test-names>
---

Plan a simulator run for `$ARGUMENTS`:

- Decide which scenarios to execute using `communication_simulator_test.py` (`--tests`, `--individual`, or full suite).
- Note required environment flags (`LOG_LEVEL=DEBUG`, provider API keys) and setup commands.
- Capture how to collect and archive logs (`--keep-logs`, `logs/mcp_server.log`).
- Outline success criteria and follow-up analysis of failures.

Format:

Summary: <headline>
Execution:
- <command(s)>
Artifacts:
- <file/path> — <why it matters>
Follow-up:
- <owner>: <action or ✅ None>
