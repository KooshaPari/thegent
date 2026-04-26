../template-commons/AGENTS.md

## External Agent Integration

thegent provides built-in support for discovering, registering, and controlling external agents via a generic black-box proxy pattern:

- **BlackBoxProxy** (`src/thegent/agents/black_box_proxy.py`) — Universal proxy for stdio/HTTP/LSP interception. Wraps external agent processes and enforces input/output policies before message forwarding.
- **Agent Discovery & Registration** (`src/thegent/cli/governance/governance_discovery_guardrails_cmds.py`) — `register_discovered_agent()` function and `discovery_scan_cmd` for auto-detecting running agent sessions (cursor-agent, Claude Code, Codex) and registering them for introspection.
- **Use Case**: Integrate external HTTP APIs (e.g., agentapi-plusplus) as discoverable agents. BlackBoxProxy can wrap HTTP calls with guardrail checks before forwarding to external services.
- **Work Package**: WP-4008 (External Agent Control & Discovery)