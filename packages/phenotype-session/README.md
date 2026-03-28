# pheno-session (prototype)

CLI + optional TUI session manager for LLM sessions across harnesses.

## Quick start

```bash
# Build
go build -o pheno-session ./...

# Run
./pheno-session list

# With SQLite
./pheno-session tui --sqlite

# Start a session
./pheno-session start --provider forge --model gpt-4o --name "my-session" --open

# Transfer a session
./pheno-session transfer sess-123 --to-harness cursor --provider cursor

# Open a session
./pheno-session open sess-123 --open-in forge
```

## Commands

- `list` — list sessions sorted by updated_by (default)
- `start` — start a new session with a provider/model
- `open` — open a session in a harness
- `transfer` — transfer a session to another harness
- `manage` — manage a session interactively (TUI)
- `tui` — run the interactive TUI for browsing sessions

## Flags

### Global
- `--config, -c` — config file path
- `--verbose, -v` — verbose output

### list
- `--harness, -H` — filter by harness (codex|forge|cursor|claude|droid)
- `--provider` — filter by provider
- `--dir` — limit to directory (off by default)
- `--all` — explicit All view (keeps dir filters off; default true)
- `--sort` — sort by (updated_by|updated_at|name; default: updated_by)
- `--limit` — max sessions to return (default: 100)
- `--json` — output JSON

### start
- `--provider` — provider to start with (required; e.g., forge)
- `--model` — model identifier (required; e.g., gpt-4o)
- `--dir` — working directory for session
- `--name` — optional session name
- `--open` — open after creation
- `--new-model` — explicitly start with a new model flow

### open
- `--open-in` — target harness (cursor|forge|codex|claude|droid)

### transfer
- `--to-harness` — target harness (required)
- `--provider` — target provider (optional)
- `--confirm` — skip confirmation prompts

## Storage

Default store: JSON at `$HOME/.local/share/phenotype/sessions.json`

Recommended store: SQLite at `$HOME/.local/share/phenotype/sessions.db`
- Use `pheno-session tui --sqlite` to force SQLite creation

Session fields:
- `id` (UUID)
- `name`
- `harness` (codex|forge|cursor|claude|droid|...)
- `provider`
- `model`
- `dir` (working directory, optional)
- `created_at`, `updated_at`
- `updated_by` (last message actor)
- `last_message`
- `state` (active|closed|paused)
- `provider_meta` (JSON metadata)

## Adapter interface

The adapter pattern allows implementation of provider-specific session management:

```go
type HarnessAdapter interface {
    ListSessions(filter SessionFilter) ([]SessionMeta, error)
    GetSession(id string) (SessionMeta, error)
    StartSession(params StartParams) (SessionMeta, error)
    TransferSession(id string, toHarness string, params map[string]any) (SessionMeta, error)
    OpenSession(id string, openIn string) error
}
```

Current implementations:
- **Forge** (stub): basic start/open flows
- **Codex, Cursor, Claude, Droid**: stubs (to be implemented)

## TUI

Run `pheno-session tui` to start an interactive session browser:

- **Up/Down (j/k)**: move selection
- **Enter**: open selected session
- **s**: cycle sort order (updated_by → updated_at → name)
- **/**: toggle filter (placeholder for now)
- **q**: quit

Default sort: `updated_by` (descending)
Default view: All sessions (directory filter off)

## Design decisions

**Language**: Go + Cobra (CLI) + Bubble Tea (TUI)
- Rationale: consistent with existing repo patterns (see bifrost-extensions/cmd/bifrost/cli/root.go and repo TUI examples)

**Storage**: SQLite for durability and performance; JSON for quick local testing
- DDL auto-applies on first run

**Adapters**: small, stable interface allows gradual implementation of provider-specific logic

**Default "All" view**: allows invocation from any directory; use `--dir` to restrict

## Next steps

1. Implement real adapters (Forge, Codex, Cursor, Claude, Droid)
2. Add interactive flows (transfer, start with new model) in TUI
3. Implement snapshot/export for session transfer
4. Add credentials/auth handling (env, keyring)
5. Integrate with existing tools in the monorepo

## References

Patterns reused from monorepo:
- Cobra CLI: bifrost-extensions/cmd/bifrost/cli/root.go
- Bubble Tea TUI: worktrees/cliproxyapi-plusplus/.../pkg/llmproxy/tui/app.go
- Codex session selection concept: helios-cli/codex-rs/tui/src/app.rs
