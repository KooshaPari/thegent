# thegent Quick Reference

One-page reference for the most common commands.

---

## Installation & Setup

| Command | Purpose |
|---------|---------|
| **Unix:** `curl -fsSL .../bootstrap.sh \| sh -s -- install` | Full bootstrap (install → setup → doctor) |
| **Windows:** `irm .../install.ps1 \| iex` | Full bootstrap (PowerShell) |
| `thegent setup` | Configure providers, install shortcuts, run wizard |
| `thegent setup --full` | Full setup: install, shims, lock-cleanup, MCP service |
| `thegent setup --agents claude,codex` | Configure only specified providers |
| `thegent install -t all` | Install to all targets (claude, cursor, shell, etc.) |
| `thegent install-shims` | Install git/rg/fd shims to ~/.local/bin |
| `thegent install-shims --prefix /opt/thegent` | Install git wrapper for system install |
| `thegent doctor` | Verify environment health |
| `thegent doctor --fix` | Attempt to fix detected issues |

---

## Running Agents

| Command | Purpose |
|---------|---------|
| `thegent run "<prompt>" free` | Run task with free-tier agent |
| `thegent run "<prompt>" -M gemini-3-flash` | Model-first routing |
| `thegent bg "<prompt>"` | Run in background |
| `thegent ps` | List active sessions |
| `thegent status` | Session status and logs |

---

## Planning & Work Stream

| Command | Purpose |
|---------|---------|
| `thegent plan do-next` | Get next actionable item |
| `thegent plan loop` | Continuous work stream processing |
| `thegent plan claim <id>` | Claim a task |
| `thegent plan complete <id>` | Mark task complete |

---

## MCP & Providers

| Command | Purpose |
|---------|---------|
| `thegent serve` | Start MCP server |
| `thegent cliproxy login <provider>` | Configure provider (claude, codex, etc.) |
| `thegent mcp up` | Start MCP via process-compose |

---

## Project Setup

| Command | Purpose |
|---------|---------|
| `thegent setup --hooks` | Install git hooks |
| `thegent setup --skills` | Sync thegent-skills to ~/.claude, ~/.cursor |

---

## Help & Maintenance

| Command | Purpose |
|---------|---------|
| `thegent --help` | Main help (includes getting started) |
| `thegent run --help` | Command-specific help |
| `thegent --install-completion zsh` | Enable shell completion |
| `thegent upgrade` | Check for newer version |
| `thegent upgrade --check` | Check only, no upgrade instructions |
