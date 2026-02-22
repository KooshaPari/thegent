# Merged Fragmented Markdown

## Source: site/guide/architecture.md

# Architecture

`thegent` is an orchestration runtime with three primary layers: execution, governance, and interface.

## Layer Overview

| Layer | Responsibility | Typical artifacts |
|------|----------------|-------------------|
| Execution | Run agent personas and workflows | `thegent run`, `thegent bg`, loop commands |
| Governance | Apply policy, quality, and budget controls | contracts, QA hooks, policy engine |
| Interface | Expose CLI + MCP tools | CLI commands, MCP server resources/tools |

## Runtime Flow

1. A command starts an agent session.
2. Hook dispatchers run pre/post checks.
3. Policy checks enforce constraints (cost, quality, safety).
4. Outputs and status are persisted for later continuation.

## Practical Design Patterns

- Keep hooks thin; move shared logic into reusable libraries.
- Keep policies data-driven in contracts, not hardcoded in command handlers.
- Prefer explicit failures over hidden fallback behavior.

## Where To Extend

- Add new persona: `agents/<name>.md`
- Add new hook: `hooks/<event>-<name>.sh`
- Add new governance policy: `contracts/<policy>.json`
- Add new CLI command: `commands/<command>/`

Use [Reference Configuration](/reference/configuration) before changing environment defaults.

---

## Source: site/guide/cli-reference.md

# CLI Reference

This page covers the core `thegent` commands used in local and CI workflows.

## Command Shape

```bash
thegent <command> [subcommand] [flags]
```

Global options are available on most commands:

- `--debug` for verbose runtime diagnostics.
- `--json` for machine-readable output where supported.
- `--help` for command-specific usage.

## Session Commands

| Command | What it does | Common usage |
|---------|---------------|--------------|
| `thegent run <prompt> [provider]` | Foreground run | One-off tasks and interactive work |
| `thegent run agent <prompt> --skill <name>` | Foreground run with selected skill instructions | Skill-guided execution |
| `thegent bg <prompt> [provider]` | Background run | Longer jobs or parallel work |
| `thegent ps` | Session list | Inspect active/recent sessions |
| `thegent stop <session_id>` | Stop session | Cancel or cleanup |
| `thegent takeover <session_id>` | Attach to session | Continue from existing context |
| `thegent run fork <session_id> [--from-turn N] [--new-session-id ID]` | Fork session history | Branch from a specific turn for alternative execution |
| `thegent run rollback <session_id> --n-turns N` | Roll back recent turns | Remove last N turns from a session |

Examples:

```bash
thegent run "audit this codepath" codex
thegent run agent "refactor this module" --skill thegent-skills
thegent bg "implement docs update" claude
thegent ps
thegent stop sess_abc123
thegent run fork sess_abc123 --from-turn 4 --new-session-id sess_branch_01
thegent run rollback sess_branch_01 --n-turns 1
```

Notes:
- `--from-turn` is 1-based and must be `>= 1`.
- `--n-turns` must be `>= 1`.

## Skill Commands

| Command | Purpose |
|---------|---------|
| `thegent skill list` | Show discovered skills |
| `thegent skill list --json` | Emit machine-readable discovered skills (stable deterministic ordering) |
| `thegent skill select <name>` | Validate skill and print `--skill` usage |

Example:

```bash
thegent skill list
thegent skill list --json
thegent skill select thegent-skills
thegent run agent "execute with selected skill" --skill thegent-skills
```

Error handling:

```bash
thegent skill select missing-skill
# Skill not found: missing-skill
```

## Planning Commands

| Command | Purpose |
|---------|---------|
| `thegent plan do-next` | Select highest-priority actionable work item |
| `thegent plan loop` | Continuously execute available tasks |
| `thegent orchestrate loop "prompt" "todo"` | Worker/checker lifecycle loop |

Example:

```bash
thegent plan do-next
thegent orchestrate loop "execute sprint tasks" "docs/reference/WORK_STREAM.md"
```

## Baseline Regression Commands

Use these commands to refresh benchmark baselines and enforce regressions in CI/local runs.

Current benchmark payloads must provide finite, non-negative `avg_microseconds` values per label.

| Command | Purpose |
|---------|---------|
| `task bench:baseline:refresh` | Regenerate `benchmarks/baseline.json` from WL-078 benchmark suite |
| `uv run python scripts/check_python_benchmark_regression.py --baseline benchmarks/baseline.json --current <path> --max-regression-pct 15` | Fail when current benchmarks regress beyond threshold |
| `uv run python scripts/check_python_benchmark_regression.py --baseline benchmarks/baseline.json --current <path> --max-regression-pct 15 --require-complete-baseline` | Also fail if any baseline labels are missing in current results |

Examples:

```bash
task bench:baseline:refresh

uv run python scripts/benchmark_python_suite.py \
  --iterations 50000 \
  --output benchmarks/results/python/latest.json \
  --overwrite

uv run python scripts/check_python_benchmark_regression.py \
  --baseline benchmarks/baseline.json \
  --current benchmarks/results/python/latest.json \
  --max-regression-pct 15

uv run python scripts/check_python_benchmark_regression.py \
  --baseline benchmarks/baseline.json \
  --current benchmarks/results/python/latest.json \
  --max-regression-pct 15 \
  --require-complete-baseline
```

## Health and Setup Commands

| Command | Purpose |
|---------|---------|
| `thegent setup` | Bootstrap credentials and runtime defaults |
| `thegent doctor` | Verify dependencies and runtime health |
| `thegent install-shims` | Install command shims into PATH |
| `thegent shell-init <bash|zsh|fish>` | Print shell integration snippet |

## MCP and Service Commands

| Command | Purpose |
|---------|---------|
| `thegent serve` | Start MCP server for clients/tools |
| `thegent mcp prune` | Cleanup stale MCP resources safely |

If you run into startup errors, use [Operations Troubleshooting](/operations/troubleshooting).

---

## Source: site/guide/getting-started.md

# Getting Started

`thegent` is a CLI and runtime for orchestrating agent tasks with operational governance.

## Prerequisites

- Python 3.12+
- Rust toolchain (for native performance components)
- Bun (for this VitePress docsite)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

## Initial Setup

```bash
thegent setup
thegent doctor
```

`thegent setup` configures provider credentials. `thegent doctor` verifies runtime health.

## First Successful Run

```bash
thegent run "summarize this repository structure" codex
```

Then inspect session status:

```bash
thegent ps
```

## Daily Workflow Example

```bash
# Find next actionable item
thegent plan do-next

# Execute one foreground task
thegent run "implement the selected item" claude

# Check and select a skill for focused runs
thegent skill list
thegent skill select thegent-skills
thegent run agent "implement with policy skill guidance" --skill thegent-skills

# Run a longer background task
thegent bg "generate implementation notes" gemini
```

## Next Reads

- [Installation](./installation)
- [CLI Reference](./cli-reference)
- [Providers](./providers)
- [Operations Troubleshooting](/operations/troubleshooting)

---

## Source: site/guide/governance.md

# Governance

`thegent` includes built-in controls so autonomous runs remain auditable and bounded.

## Governance Surfaces

- Cost controls: provider/model routing and spend-sensitive policies.
- Quality gates: lint, tests, and policy checks on lifecycle events.
- Security checks: secret scanning and static analysis in validation pipelines.
- Operational safety: explicit session lifecycle and auditable history.

## Baseline Policy Workflow

```bash
# 1) Verify runtime health
thegent doctor

# 2) Execute work
thegent run "implement feature and tests" codex

# 3) Validate and review state
thegent ps
thegent plan do-next
```

## Recommended Team Defaults

| Area | Recommendation |
|------|----------------|
| Routing | Use explicit provider/model for critical jobs |
| Budgets | Enforce environment-level spend caps |
| Validation | Run quality checks on each merge candidate |
| Recovery | Prefer continuation/takeover over restarting context |

## Common Pitfalls

- Running long loops without policy or budget constraints.
- Mixing unrelated workstreams in a single session.
- Bypassing hook-based validation.

See [Operations Runbooks](/operations/runbooks) for remediation steps.

---

## Source: site/guide/installation.md

# Installation

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Required |
| Rust | stable | Required for native extensions |
| Bun | latest | Needed for docsite dev/build |

## Install Methods

### Bootstrap Script (recommended)

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install

# Windows (PowerShell)
irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
```

### pip

```bash
pip install thegent
```

### From Source

```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent install -t all
thegent install-shims
thegent setup --hooks
```

## Shell Integration

```bash
# zsh
echo 'eval "$(thegent shell-init zsh)"' >> ~/.zshrc
source ~/.zshrc
```

## Verify

```bash
thegent doctor
thegent run "installation smoke test" free
```

If verification fails, continue with [Operations Troubleshooting](/operations/troubleshooting).

---

## Source: site/guide/providers.md

# Providers

`thegent` can route work across direct APIs and proxy-backed providers.

## Supported Provider Labels

| Provider | Typical default | Notes |
|----------|------------------|-------|
| `free` | `gpt-5-mini` | default convenience route |
| `claude` | `claude-haiku-4.5` | Anthropic API |
| `codex` | `gpt-5.3-codex` | OpenAI/Codex API |
| `gemini` | `gemini-3-flash` | Google API |
| `cursor` / `kiro` / custom | varies | proxy-dependent |

## Credential Setup

```bash
thegent setup --provider claude
thegent setup --provider codex
thegent setup --provider gemini
```

Manual env setup:

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
export GOOGLE_API_KEY="..."
```

## Practical Routing Patterns

```bash
# Explicit provider
thegent run "generate migration checklist" --provider claude

# Explicit model
thegent run "deep code audit" -M gpt-5.3-codex

# Cost-aware automatic routing
thegent run "summarize logs" -R cheapest
```

## Proxy Provider Example

```bash
thegent config set providers.myproxy.url "http://localhost:8317"
thegent config set providers.myproxy.model "claude-sonnet-4-6"
thegent run "health check" --provider myproxy
```

## Failure Handling

- Re-run failing commands with `--debug`.
- Confirm credentials are loaded in the active shell.
- Use [Routing Reference](/reference/routing) for route decision behavior.

---
