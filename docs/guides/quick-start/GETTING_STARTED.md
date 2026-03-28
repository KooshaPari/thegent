# Getting Started with thegent

thegent is a unified agent orchestration system. It lets you spawn, direct, and
coordinate AI coding agents (Claude, GPT, Gemini, and others) from a single CLI,
manage sessions, track work via a DAG-based roadmap, and enforce governance
policies.

---

## Prerequisites

Before installing thegent, ensure the following are present on your system:

- **Python 3.11 or later.** thegent uses modern Python typing features.
- **pip or uv.** Either package manager works; `uv` is faster for fresh installs.
- **At least one LLM provider API key.** The most common starting point is an
  Anthropic API key for Claude.

Optional but recommended:

- **git 2.35 or later** — required for the worktree governance commands.
- **A supported shell** — bash, zsh, or fish for shell completion.

---

## Installation

### Using pip

```bash
pip install thegent
```

### Using uv (recommended for speed)

```bash
uv pip install thegent
```

### Verify the installation

```bash
thegent --version
```

You should see a version string printed to stdout. If the command is not found,
ensure your Python `bin` directory is on `PATH`.

---

## First-Time Setup

Run the interactive setup wizard to configure providers and install system
integrations:

```bash
thegent setup
```

The wizard will walk you through:

1. Entering API keys for the providers you want to use.
2. Selecting a default agent and model.
3. Optionally installing shell shortcuts (`claudeglm`, `claudemax`).
4. Optionally installing git hooks for pre-commit checks.
5. Optionally syncing thegent skill templates to `~/.claude` and `~/.cursor`.

To skip the interactive prompts and configure Claude only from the command line:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
thegent setup --no-wizard --agents claude
```

For a full system installation that includes the MCP service, harness, and all
shims:

```bash
thegent setup --full
```

---

## Environment Variables

The setup wizard saves credentials to a local config file. You can also supply
them directly via environment variables, which take precedence:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export THEGENT_PROVIDER=claude
```

Set these in your shell profile (`~/.zshrc`, `~/.bashrc`, etc.) to persist them
across sessions.

---

## Your First Agent Run

Once setup is complete, run a one-shot task using the default agent:

```bash
thegent do "Explain what this repository does"
```

For a longer task that should continue in the background:

```bash
thegent run bg "Add comprehensive unit tests to the payment module" \
  --agent claude \
  --model sonnet
```

This enqueues a background session. Check on it at any time:

```bash
thegent session list
```

Resume the most recent session if you want to provide follow-up instructions:

```bash
thegent session resume
```

---

## Common Use Cases

### Running a code review

```bash
thegent review "Review the authentication service for security vulnerabilities"
```

The review command runs the agent in a read-only mode and returns structured
findings.

### Managing a multi-step project roadmap

Add tasks to the DAG:

```bash
thegent plan add T-001 --prompt "Design the new data model" --agent claude
thegent plan add T-002 --prompt "Implement migration scripts" --dep T-001
thegent plan add T-003 --prompt "Write integration tests" --dep T-002
```

Check which tasks are ready to run:

```bash
thegent plan next
```

View the full dependency graph:

```bash
thegent plan status --format graph
```

### Running multiple agents as a crew

Create a crew for a coordinated refactoring task:

```bash
thegent crew create --name "refactor-crew" --mode sequential
```

Add agents with distinct roles:

```bash
thegent crew add-agent <crew-id> --role architect --name "Planner"
thegent crew add-agent <crew-id> --role implementer --name "Builder"
```

Add tasks:

```bash
thegent crew add-task <crew-id> --description "Audit the existing codebase"
thegent crew add-task <crew-id> \
  --description "Implement the hexagonal refactor" \
  --dependencies <task-id>
```

Execute:

```bash
thegent crew execute crew-definition.json
```

### Checking system health

```bash
thegent audit doctor
```

For a full audit across health, security, and planning:

```bash
thegent audit all --severity high
```

### Using skills

Skills are named instruction sets that tune an agent for a specific task
pattern. Activate one or more with the `--skill` flag:

```bash
thegent run agent "Refactor this module" --skill hexagonal
thegent run bg "Write a migration" --skill sql --skill tdd
```

List available skills:

```bash
thegent skill list
```

---

## Checking Logs and Session History

View recent run history:

```bash
thegent run history
```

List all sessions:

```bash
thegent session list --all
```

Inspect session contract health (useful in CI):

```bash
thegent session-contract-health-gate --min-healthy-ratio 0.9
```

---

## Shell Completion

Install shell completion for your shell:

```bash
thegent --install-completion
```

Restart your terminal or source your shell profile for the completion to take
effect.

---

## Troubleshooting

### `thegent: command not found`

Your Python `bin` directory is not on `PATH`. Find it with:

```bash
python -m site --user-base
```

Then add `<user-base>/bin` to your `PATH` in your shell profile.

### `ANTHROPIC_API_KEY not set` or similar errors

Export the required key before running:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
thegent do "hello"
```

Or run `thegent setup` to configure it persistently.

### Git coordination unavailable

The git subcommands require the optional `thegent-git` package:

```bash
pip install thegent-git
```

### Doctor reports missing dependencies

Run the doctor with the fix flag to attempt automatic remediation:

```bash
thegent doctor --fix
```

If issues persist, review the output for specific missing tools and install them
using your system package manager.

### Background session is stuck or unresponsive

List sessions to find the stuck session ID, then resume with a follow-up prompt:

```bash
thegent session list
thegent session resume <session-id> --prompt "Are you still running?"
```

---

## Next Steps

- Read the full [CLI Reference](../../reference/CLI_REFERENCE.md) for all
  available commands and flags.
- Explore `thegent plan` for DAG-based work management.
- Configure routing strategies with `thegent routing` to balance cost and
  capability across providers.
- Use `thegent dotfiles deploy` to synchronize tool configurations across
  machines.
