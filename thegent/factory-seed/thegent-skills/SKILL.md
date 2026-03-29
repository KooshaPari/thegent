# Thegent Skills

Unified orchestration guidance for external agents using `thegent` as the default execution path.

## Primary Rule

Use `thegent` subcommands, not legacy positional form.

- Required: `thegent run [options] "<prompt>" [agent]` (prompt-first; agent optional with `-M`/`--model-first`)
- Required for long jobs: `thegent bg ...`, then `thegent status`, `logs`, `wait`, `stop`
- Do not use: wrapper scripts or `thegent <agent> <prompt>`.

## Installation / Upgrade

Canonical standalone project path (replace with your checkout path if moved):

`/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent`

Install or refresh globally:

```bash
uv tool install --editable /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent
```

Verify:

```bash
thegent --help
thegent run --help
thegent list-agents
```

For minimax/glm: install `codexmax` and `codexglm` to `~/.local/bin` (see project `scripts/`), ensure `codex` CLI and `~/.factory/config.json` with MiniMax-M2.5/GLM-5 entries.

Tip: install with an environment-independent root variable:

```bash
export THEGENT_ROOT=/path/to/kush/thegent
uv tool install --editable "$THEGENT_ROOT"
```

## Standard Invocation

```bash
# Foreground
thegent run -d /path/to/repo -m write -t 120 "Analyze and summarize risks" cursor-agent
thegent run -d /path/to/repo -m read-only -t 90 "List critical modules" gemini

thegent run -d /path/to/repo -m write -M gemini-3-pro-preview "Deep analysis"

thegent run -d /path/to/repo -m read-only -P antigravity -M claude-sonnet-4 "Architecture review"
```

## Option Ordering (Typer-safe)

Use options first to avoid positional ambiguity:

```bash
thegent run -d "/path/to/repo" -m read-only -t 60 gemini "List top modules"
thegent bg -d "/path/to/repo" -m write -t 600 --full "Draft design notes" minimax
```

## Session Register / Inbox

For deterministic orchestration, treat `owner` as a session inbox key:

```bash
export THGENT_OWNER_TAG="agent-orch:${USER}:$(basename "$PWD"):$(date +%s)"

thegent bg --format json --owner "$THGENT_OWNER_TAG" -d /path/to/repo -m write "Implement feature X" cursor-agent
thegent ps --owner "$THGENT_OWNER_TAG" --format json
thegent inspect --owner "$THGENT_OWNER_TAG" --format json

# Parse newest session id
SESSION_ID="$(thegent ps --owner "$THGENT_OWNER_TAG" --format json | python -c 'import json,sys; j=json.load(sys.stdin); print(j[-1]["id"])')"
thegent logs "$SESSION_ID" --follow
thegent status "$SESSION_ID" --format json
```

## Long-Running / Observable Invocation

```bash
# Use one explicit owner for the full session family (stable across status checks)
export THGENT_OWNER_TAG="agent-orch:${USER}:$(basename "$PWD"):$(date +%s)"

SESSION_JSON="$(thegent bg --format json -d /path/to/repo --owner "$THGENT_OWNER_TAG" -m write -t 600 --full "Implement feature X" cursor-agent)"
SESSION_ID="$(printf '%s' "$SESSION_JSON" | python -c 'import json, sys; print(json.load(sys.stdin)["session_id"])')"

# Monitor by explicit owner scope
thegent ps --owner "$THGENT_OWNER_TAG"
thegent status "$SESSION_ID"
thegent inspect --owner "$THGENT_OWNER_TAG" --format json
thegent logs --follow "$SESSION_ID"
thegent logs --follow --timeout 30 "$SESSION_ID"

# Completion / control
thegent wait -t 1800 "$SESSION_ID"   # exit code is authoritative
thegent stop "$SESSION_ID"
thegent stop --force "$SESSION_ID"
```

## Agent Selection Guidance

- Prefer native tool-specific subagents only when a tool-only capability is required.
- Prefer `thegent` for cross-provider consistency, model override, and session observability.
- **Agents:** gemini, codex, copilot, cursor-agent, claude, minimax, glm

## Models

```bash
thegent list-models
thegent list-models cursor-agent
thegent list-models minimax
thegent list-models glm
```

## Reliability Notes

- Use `--owner` for predictable session scoping across concurrent agents.
- Use `--full` in `bg` for raw logs when debugging.
- Reuse `THGENT_OWNER_TAG` across `bg`, `ps`, `inspect`, and `status` calls.
- Treat `thegent wait` exit code as the authoritative automation result.
