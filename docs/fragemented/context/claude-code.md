# Claude Code CLI Context

> Definitive reference for implementing Claude Code support in thegent (agent harness integration, CLI subprocess execution, tool system interop).
> Sources: claude.ai/install.sh, @anthropic-ai/claude-code npm package, official documentation, GitHub anthropics/claude-code (fetched 2026-02-20).

---

## What is Claude Code

Claude Code is Anthropic's official agentic coding harness: a command-line interface that provides conversational access to Claude AI models directly from the terminal. Unlike web-based interfaces, Claude Code:

- Maintains full codebase context with deep file system access
- Executes real filesystem, git, and shell operations without manual approval
- Supports Model Context Protocol (MCP) servers for external tool integration
- Spawns parallel subagents (up to 7) for decomposed task execution
- Integrates git workflows (branch creation, commits, pull requests) natively
- Provides extensibility through slash commands, skills, and custom hooks

Claude Code is specifically designed for pair-programming workflows: helping developers understand complex code, execute routine tasks, implement features, debug, test, and manage CI/CD workflows.

**Key distinction**: Claude Code is the harness/CLI, not an LLM. It wraps Anthropic's Claude models (Haiku, Sonnet, Opus) with tooling, persistence, and agent orchestration.

---

## Installation & Authentication

### Installation Methods

**Option 1: Native binary (recommended)**
```bash
# macOS/Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

**Option 2: npm (legacy, requires Node.js 18+)**
```bash
npm install -g @anthropic-ai/claude-code
```

### Authentication

Claude Code requires a valid Claude subscription:
- **Claude Pro**: $20/month (includes API access)
- **Claude Max**: $100-200/month (higher rate limits)
- **Teams/Enterprise**: Via Anthropic

Authentication uses your `ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
claude "your query"
```

API keys are created in the [Anthropic Console](https://console.anthropic.com/keys).

---

## Core CLI Usage

### Interactive Mode (Default)

```bash
claude "your natural language query"
```

Launches a conversational session where Claude can run multiple agentic turns until the task is complete. Supports:
- File operations (read, write, edit)
- Shell command execution
- File globbing and search
- Git operations
- Web research
- Tool invocation

Exit with `Ctrl+C` or by responding "done" to the agent.

### Non-Interactive Mode (--print)

```bash
claude -p "query"
```

Executes a single query and exits, printing results to stdout. Useful for:
- Scripting and batch automation
- CI/CD integration
- Piping output to other commands
- One-shot analysis tasks

Does not enter conversation loop; all work is completed in a single agent execution window.

### Session Management

| Command | Purpose |
|---------|---------|
| `claude` | Start new session |
| `claude -c` / `--continue` | Resume most recent session |
| `claude --resume <session-id>` | Resume specific prior session |

---

## Key CLI Flags

### Output & Format

| Flag | Values | Description |
|------|--------|-------------|
| `-p`, `--print` | boolean | Non-interactive mode; single query and exit |
| `--output-format` | `text`, `json`, `stream-json` | Response format |

**Output format details**:
- `text`: Plain text; default for interactive mode
- `json`: Full response with metadata as JSON object
- `stream-json`: Streaming JSONL format; one JSON object per message as it arrives (useful for real-time processing)

**Example**:
```bash
claude -p --output-format json "List TypeScript files"
```

```json
{"type":"message","content":"Found the following TypeScript files:...","tool_calls":[]}
{"type":"tool_result","name":"glob","content":"src/index.ts src/utils.ts..."}
```

### Model Selection

| Flag | Values | Description |
|------|--------|-------------|
| `--model` | `haiku`, `sonnet`, `opus`, or full model name | Which Claude model to use |

**Examples**:
```bash
claude --model opus "complex analysis task"
claude --model haiku "simple file listing"
claude --model claude-opus-4-20250514 "specific version"
```

Default: `sonnet` (balanced cost/capability). Use `opus` for complex reasoning; `haiku` for simple, fast tasks.

### Agent Control

| Flag | Values | Description |
|------|--------|-------------|
| `--max-turns` | integer | Maximum agent conversation turns (default: unlimited) |
| `--allow-subagents` | boolean | Enable spawning parallel subagents (default: true) |

**Example**:
```bash
claude --max-turns 10 "refactor this codebase"
```

Prevents runaway agentic loops. Useful for controlling costs in CI/CD.

### Tool & Permission Control

| Flag | Values | Description |
|------|--------|-------------|
| `--allowedTools` | comma-separated list | Whitelist of tools; only these can be called |
| `--disallowedTools` | comma-separated list | Blacklist of tools; these are forbidden |
| `--permission-mode` | `auto`, `manual` | Auto-approve actions or request permission for each |
| `--dangerously-skip-permissions` | boolean | Skip all permission checks (dangerous; CI/CD only) |

**Tools available** (can be controlled):
- `bash`: Shell command execution
- `read_file`: File read (read-only)
- `write_file`: File creation
- `edit_file`: File modification (precise edits)
- `glob`: File pattern matching
- `grep`: Content search
- `web_search`: Internet research
- `git_*`: Git operations (branch, commit, pr, etc.)

**Example**:
```bash
claude --disallowedTools bash,web_search "refactor code without shell access"
```

---

## Configuration System

Claude Code uses a hierarchical configuration system, with later entries overriding earlier ones:

1. **Organizational policies** (enterprise only)
2. **Project shared** (`.claude/settings.json`)
3. **Project local** (`.claude/settings.local.json`)
4. **User global** (`~/.claude/settings.json`)

### Configuration File Format

```json
{
  "modelName": "sonnet",
  "maxTokens": 8000,
  "maxTurns": 20,
  "tools": {
    "allowedTools": ["bash", "read_file", "write_file", "git_*"],
    "disallowedTools": [],
    "permissionMode": "manual"
  },
  "mcpServers": [
    {
      "name": "postgres",
      "command": "node",
      "args": ["~/mcp-servers/postgres/index.js"]
    }
  ],
  "hooks": {
    "preToolUse": ["scripts/pre-tool-check.sh"],
    "postToolUse": ["scripts/post-tool-cleanup.sh"]
  },
  "extendedThinking": true,
  "memory": {
    "enabled": true,
    "persistenceFile": ".claude/memory.json"
  }
}
```

### Key Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `modelName` | string | Claude model to use (haiku, sonnet, opus) |
| `maxTokens` | integer | Max output tokens per response |
| `maxTurns` | integer | Max agentic turns before stopping |
| `tools.allowedTools` | array | Whitelist of tools |
| `tools.disallowedTools` | array | Blacklist of tools |
| `tools.permissionMode` | enum | `auto` or `manual` (request per action) |
| `mcpServers` | array | MCP server configurations |
| `hooks` | object | Lifecycle event hooks (see below) |
| `extendedThinking` | boolean | Enable Claude's extended reasoning mode (default: true) |
| `memory.enabled` | boolean | Persist conversation memory across sessions |

---

## Project Memory (CLAUDE.md)

Claude Code searches for `.claude/CLAUDE.md` files at project root and parent directories, using them as persistent project context. This file should contain:

- Project architecture and key concepts
- Development standards and conventions
- Common workflows and patterns
- Known limitations or gotchas
- Integration instructions for external tools

Example:
```markdown
# My Project

## Architecture
- Backend: Node.js/Express (src/server/)
- Frontend: React (src/client/)
- Database: PostgreSQL with Prisma ORM

## Standards
- Use TypeScript for all code
- Follow ESLint config in .eslintrc.json
- All PRs require tests

## Quick Start
1. npm install
2. npm run dev
3. Visit http://localhost:3000
```

Claude Code loads and references this automatically, improving code decisions and reducing token waste explaining basics.

---

## Hooks System

Claude Code supports event-driven hooks for lifecycle management. Hooks are shell scripts triggered at specific points in the agent execution.

### Hook Events

| Event | Fires When | Pass Arguments |
|-------|-----------|-----------------|
| `PreToolUse` | Before any tool invocation | tool name, tool arguments (JSON) |
| `PostToolUse` | After tool completes | tool name, exit code, result |
| `UserPromptSubmit` | Before processing user input | prompt text |
| `Stop` | Agent session ends | exit reason, task summary |
| `SessionStart` | New session begins | session metadata |

### Hook Registration

In `.claude/settings.json`:
```json
{
  "hooks": {
    "preToolUse": ["scripts/pre-tool-check.sh"],
    "postToolUse": ["scripts/post-tool-cleanup.sh"],
    "stop": ["scripts/cleanup.sh"]
  }
}
```

### Hook Script Example

`scripts/pre-tool-check.sh`:
```bash
#!/bin/bash
tool_name=$1
tool_args=$2

# Reject bash if running in CI
if [[ "$tool_name" == "bash" && "$CI" == "true" ]]; then
  echo "error: bash forbidden in CI"
  exit 1
fi

exit 0
```

---

## MCP (Model Context Protocol) Integration

Claude Code supports MCP servers for connecting to external tools: databases, cloud services, APIs, local file systems, version control systems.

### MCP Configuration

In `.claude/settings.json`:

```json
{
  "mcpServers": [
    {
      "name": "postgres",
      "command": "node",
      "args": ["~/.mcp-servers/postgres.js"],
      "env": {
        "DATABASE_URL": "postgresql://..."
      },
      "timeout": 5000,
      "transport": "stdio"
    },
    {
      "name": "github",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    }
  ]
}
```

### Supported MCP Transports

| Transport | Use Case | Notes |
|-----------|----------|-------|
| `stdio` | Local tools, CLI apps | Most common; subprocess over stdin/stdout |
| `sse` | HTTP servers | Server-sent events; stateful connections |
| `websocket` | Browser-like clients | Real-time bidirectional communication |

### MCP Tool Discovery

After configuring MCP servers, available tools are automatically discovered and exposed. Example: Postgres MCP server provides tools like `query_database`, `execute_transaction`, etc.

```bash
claude "Query my postgres database for user count"
```

Claude automatically invokes the Postgres MCP tool without explicit configuration.

---

## Tool System

### Built-In Tools (Always Available)

| Tool | Purpose | Permissions |
|------|---------|-----------|
| `read_file` | Read file contents | Requires read permission |
| `write_file` | Create or overwrite file | Requires write permission |
| `edit_file` | Precise edits (character ranges) | Requires write permission |
| `glob` | Pattern-based file finding | Read-only |
| `grep` | Content search (regex) | Read-only |
| `bash` | Shell command execution | Dangerous; gated |
| `git_*` | Git operations (branch, commit, status, pr, etc.) | Gated; requires git repo |
| `web_search` | Internet research via Exa API | Requires API key |

### Tool Invocation in Prompts

Claude Code automatically detects when tools are needed and invokes them. You can hint at tool use:

```bash
claude "Find all Python files with 'async def' using glob and grep"
```

Alternatively, force tool invocation with special syntax:

```bash
claude "@path/to/file.py show me the main function"
# References specific file in context
```

### Tool Approval Flow

With `permissionMode: manual` (default):

1. Agent identifies tool need
2. Claude Code requests user approval
3. User approves or denies
4. If approved, tool executes and result feeds back to agent
5. If denied, agent continues without that tool

With `permissionMode: auto`: Tools execute immediately without prompting.

---

## Stdin Input & Piping

Claude Code accepts input via stdin for scripting:

```bash
echo "analyze this code:" | cat - myfile.py | claude --output-format json
```

Or from a file:

```bash
claude < input_prompt.txt
```

Useful for:
- Batch analysis
- Shell pipeline integration
- Pulling prompts from templates
- CI/CD automation

---

## Subagents (Task Parallelization)

Claude Code can spawn up to 7 parallel subagents for decomposed task execution:

```bash
claude "Refactor the API, frontend, and database schema in parallel"
```

Claude automatically:
1. Breaks task into subtasks
2. Spawns subagents for each
3. Coordinates execution
4. Merges results

Controlled via:

| Flag | Description |
|------|-------------|
| `--allow-subagents true/false` | Enable/disable subagent spawning |
| `--max-parallel` | Max concurrent subagents (default: 7) |

---

## Non-Interactive / Subprocess Execution (Python)

To use Claude Code as a subprocess from Python:

```python
import subprocess
import json

result = subprocess.run(
    ["claude", "-p", "--output-format", "json", "Find all TODO comments"],
    capture_output=True,
    text=True,
    env={**os.environ, "ANTHROPIC_API_KEY": api_key}
)

output = json.loads(result.stdout)
todo_comments = output["content"]  # Tool results embedded
exit_code = result.returncode
```

### Streaming Mode (stream-json)

For large operations, use streaming to process results incrementally:

```python
import subprocess
import json

process = subprocess.Popen(
    ["claude", "-p", "--output-format", "stream-json", "Refactor entire codebase"],
    stdout=subprocess.PIPE,
    text=True,
    env={**os.environ, "ANTHROPIC_API_KEY": api_key}
)

for line in process.stdout:
    if line.strip():
        event = json.loads(line)
        if event["type"] == "message":
            print(f"Claude: {event['content']}")
        elif event["type"] == "tool_result":
            print(f"Tool {event['name']}: {event['content']}")

exit_code = process.wait()
```

---

## Exit Codes & Error Handling

| Code | Meaning | Recovery |
|------|---------|----------|
| `0` | Success | Task completed normally |
| `1` | General error | Check stderr for details |
| `2` | Permission denied | User rejected tool use or insufficient permissions |
| `3` | API error | API key invalid, rate limited, or quota exceeded |
| `4` | Timeout | Task exceeded max-turns or wall-clock timeout |
| `5` | Invalid arguments | CLI args malformed or invalid |
| `130` | Interrupted (SIGINT) | User pressed Ctrl+C |

**Always check stderr** for detailed error messages:

```bash
claude "query" 2>&1 | tee claude.log
echo "Exit code: $?"
```

---

## Git Integration

Claude Code is deeply integrated with git:

```bash
claude "Create a feature branch, implement user auth, and commit with good messages"
```

Available git operations:
- `git_branch_create`: Create and switch to new branch
- `git_status`: Check repo status
- `git_diff`: Show changes
- `git_add`: Stage files
- `git_commit`: Commit with message
- `git_push`: Push to remote
- `git_pull_request`: Create PR (via GitHub API)

Example:
```bash
claude "Fix the bug in auth.js (see the error in logs), commit, and create a PR"
```

Claude will:
1. Read auth.js
2. Analyze the error context
3. Implement fix
4. Add and commit
5. Push to a new branch
6. Create GitHub PR with description

---

## Extended Thinking (Reasoning Mode)

By default, Claude Code uses extended thinking for complex reasoning tasks:

```json
{
  "extendedThinking": true
}
```

This enables Claude to think through problems carefully before responding. Consumes more tokens but produces higher-quality results for complex tasks (architecture decisions, debugging, code reviews).

Disable with:

```bash
claude --disable-extended-thinking "list files quickly"
```

---

## Model Selection Best Practices

| Task | Recommended | Reasoning |
|------|------------|-----------|
| Complex refactoring | `opus` | Reasoning, large context, API design |
| Feature implementation | `sonnet` | Good balance; 200k context |
| Bug fixes | `sonnet` or `haiku` | Depends on complexity |
| Code analysis/review | `opus` | Nuanced judgment |
| File operations | `haiku` | Fast, cheap, sufficient |
| One-shot tasks | `haiku` | Minimize cost |

---

## How thegent Integrates Claude Code

thegent uses Claude Code as one of its primary harnesses via:

1. **Subprocess execution**: Spawns `claude -p --output-format json` for batch execution
2. **MCP forwarding**: Exposes thegent MCP tools to Claude Code via `.claude/settings.json`
3. **Configuration propagation**: Passes thegent governance policies to Claude Code via hooks and settings
4. **Session coordination**: Manages Claude Code sessions through the agent orchestration layer
5. **Cost tracking**: Routes API keys and tracks usage through CLIProxyAPIPlus

**Key integration point**: thegent wraps Claude Code invocations to provide:
- Unified model routing
- Cost aggregation across harnesses
- Governance enforcement (approval policies, sandbox modes)
- MCP tool registry management
- Session state persistence

---

## Common Workflows

### Analyze Codebase + Generate Report

```bash
claude "Analyze our src/ directory for architectural issues, security concerns, and performance problems. Provide a structured report."
```

### Test-Driven Development

```bash
claude "Write failing tests for the user login feature in test/auth.test.ts, then implement the feature in src/auth.ts"
```

### Debugging with Context

```bash
claude "Debug this error: $(cat error.log). The stack trace shows lib/parser.js:42. What's wrong?"
```

### Parallel Code Review

```bash
claude "Review the API endpoints (src/api/), database schema (db/), and frontend components (src/components/) in parallel for best practices"
```

### Batch Refactoring

```bash
claude --max-turns 15 "Refactor all TypeScript files to remove deprecated lodash methods. Use native ES6 alternatives."
```

---

## Key Differences from Web Claude

| Feature | Web Claude | Claude Code CLI |
|---------|-----------|-----------------|
| File system access | Upload/download only | Deep, bidirectional |
| Git integration | Manual workflows | Native branch/commit/PR |
| Tool availability | Limited (web tools only) | All tools + MCP servers |
| Session persistence | Per-browser | Cross-session memory |
| Automation | Interactive only | Scriptable via CLI |
| MCP servers | Not supported | Full support |
| Subagents | No | Up to 7 parallel |
| Speed | Fast but single-threaded | Parallel execution possible |
| Cost | Per-token | Per-token (same models) |

---

## Relevant to thegent Because

thegent integrates Claude Code as a primary harness for:

1. **Coding tasks**: thegent routes code-related work to Claude Code via task spawning
2. **Tool orchestration**: Claude Code's MCP server system aligns with thegent's MCP tool registry
3. **Governance**: thegent's policy engine coordinates with Claude Code's hooks and permission modes
4. **Cost tracking**: API calls through Claude Code are aggregated into thegent's usage reports
5. **Agent coordination**: thegent orchestrates multiple Claude Code instances for parallel work
6. **Configuration**: Project-level `.claude/settings.json` integrates with thegent's global CLAUDE.md

---

## Sources

- [Claude Code Overview](https://code.claude.com/docs/en/overview)
- [Claude Code MCP Integration](https://code.claude.com/docs/en/mcp)
- [Shipyard Claude Code Cheat Sheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [Claude Code CLI Reference (2025)](https://www.eesel.ai/blog/claude-code-cli-reference)
- [Claude Code Complete Guide 2026](https://www.jitendrazaa.com/blog/ai/claude-code-complete-guide-2026-from-basics-to-advanced-mcp-2/)
- [GitHub: anthropics/claude-code](https://github.com/anthropics/claude-code)
- [Building Agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
