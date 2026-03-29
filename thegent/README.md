# thegent

This repository works with Claude and other AI agents as autonomous software engineers.

## Quick Start

```bash
# Install
pip install thegent

# Run
thegent run --agent claude

# Or use as library
from thegent import Agent
agent = Agent(provider="claude")
```

## Multi-Agent Orchestration

Control multiple agents via CLI or API:

```bash
# Start agent
thegent run --agent claude --model sonnet

# List available agents
thegent agents list

# Session management
thegent session list
thegent session resume <id>
```

### Agent Selection

| Agent | Command | Models |
|-------|---------|---------|
| Claude | `--agent claude` | sonnet, opus, haiku |
| GPT | `--agent openai` | gpt-4o, o1, o3 |
| Gemini | `--agent gemini` | pro, flash |
| Claude Code | `--agent codex` | codex-default |

## Environment

```bash
export ANTHROPIC_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."
export THEGENT_PROVIDER=claude
```

---

## Development Philosophy

### Extend, Never Duplicate

- NEVER create a v2 file. Refactor the original.
- NEVER create a new class if an existing one can be made generic.
- NEVER create custom implementations when an OSS library exists.
- Before writing ANY new code: search the codebase for existing patterns.

### Primitives First

- Build generic building blocks before application logic.
- A provider interface + registry is better than N isolated classes.
- Template strings > hardcoded messages. Config-driven > code-driven.

### Research Before Implementing

- Check PyPI for existing libraries.
- Search GitHub for 80%+ implementations to fork/adapt.

---

## Library Preferences (DO NOT REINVENT)

| Need | Use | NOT |
|------|-----|-----|
| HTTP client | httpx | Custom wrappers |
| CLI | typer | argparse |
| Config | pydantic-settings | Manual env parsing |
| Validation | pydantic | Manual if/else |
| Async | asyncio | Threading without reason |
| Caching | PersistDict | Custom cache |

---

## Code Quality Non-Negotiables

- Zero new lint suppressions without inline justification
- All new code must pass: ruff, mypy, tests
- Max function: 40 lines
- No placeholder TODOs in committed code

### Python-Specific Rules

- Use `ruff` for formatting and linting
- Use `mypy` for type checking
- All public APIs must have type hints

---

## Verifiable Constraints

| Metric | Threshold | Enforcement |
|--------|-----------|-------------|
| Tests | 80% coverage | pytest --cov |
| Lint | 0 errors | ruff check |
| Type check | 0 errors | mypy |

---

## Domain-Specific Patterns

### What thegent Is

thegent is an **agent orchestration framework** that provides CLI and Python APIs for managing AI agent workflows, multi-agent swarms, and governance. The core domain is: provide a unified interface to spawn, control, and coordinate multiple AI agents.

### Key Interfaces

| Interface | Responsibility | Location |
|-----------|----------------|----------|
| **CLI** | Command-line interface | `src/thegent/cli/` |
| **Agent** | Agent abstraction | `src/thegent/agents/` |
| **Governance** | Policy enforcement | `src/thegent/governance/` |
| **MCP** | Tool integration | `src/thegent/mcp/` |
| **Execution** | Task running | `src/thegent/execution/` |

### Architecture Layers

```
1. CLI Layer (typer)
2. Agent Abstraction
3. Provider Router (cliproxy++)
4. Tool System (MCP)
5. Governance/Policy
6. Execution Engine
```

### Common Anti-Patterns to Avoid

- **Hardcoded provider logic** -- Use router abstraction
- **Blocking on agent response** -- Use streaming/async
- **No governance** -- Always add policy checks
- **Missing session state** -- Agents maintain conversation context

---

## Kush Ecosystem

This project is part of the Kush multi-repo system:

```
kush/
├── thegent/         # Agent orchestration (this repo)
├── agentapi++/      # HTTP API for coding agents
├── cliproxy++/      # LLM proxy with multi-provider support
├── tokenledger/     # Token and cost tracking
├── 4sgm/           # Python tooling workspace
├── civ/             # Deterministic simulation
├── parpour/         # Spec-first planning
└── pheno-sdk/       # Python SDK
```

---

## License

MIT License - see LICENSE file
