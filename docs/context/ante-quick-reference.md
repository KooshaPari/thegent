# ANTE Quick Reference Guide

A rapid reference for ANTE (Another Terminal) terminal AI agent for developers and integrators.

## One-Liner

ANTE is a lightweight, native Rust terminal AI agent by Antigma Labs. Provider-agnostic, security-focused, with extensible skills and sub-agents.

## Installation & First Use

```bash
# Install
brew install ante  # or build from source

# First prompt (under 1 minute)
ante
# or
ante run "Your prompt here"
```

## Architecture at a Glance

```
Client (TUI/Headless) ←→ Daemon (Sessions, Tools, Providers)
                        ↓
                   LLM Provider (Claude, GPT-4, Gemini, Grok, Local)
```

**Key Components:**
- **Session**: Isolated execution context
- **Turn**: Agent-user exchange with tool execution
- **Tool**: Executable capability (File I/O, Shell, Web, etc.)
- **Skill**: Custom extension (user or project-level)
- **Provider**: LLM backend abstraction

## Supported LLM Providers

| Provider | Models | Wire Format | Auth |
|----------|--------|-------------|------|
| Anthropic | Claude | Messages API | ENV var / OAuth |
| OpenAI | GPT-4o, o1 | Chat Completions | ENV var / OAuth |
| Gemini | Gemini family | Native API | ENV var |
| Grok | Grok models | OpenAI-compatible | ENV var |
| Open Router | Multi | OpenAI-compatible | ENV var |
| Local | GGUF (llama.cpp) | Local inference | File path |

Set via: `--provider NAME --model MODEL` or `~/.ante/settings.json`

## Built-in Tools

**File I/O**: Read, Write, Edit, Glob, Grep

**Shell**: Bash (approval required), BashOutput, KillShell

**Web**: WebFetch, WebSearch

**Agent**: Task (spawn sub-agent), TodoWrite

Filter tools: `--allowed-tools Read,Write,Bash`

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=...     # Anthropic auth
OPENAI_API_KEY=...        # OpenAI auth
ANTE_HOME=~/.ante         # Config directory
ANTE_DEBUG=1              # Debug logging
NO_COLOR=1                # Disable colors
```

### Settings File

`~/.ante/settings.json`:

```json
{
  "model": "claude-opus-4.6",
  "provider": "anthropic",
  "theme": "dark",
  "context_limit": 100000,
  "allowed_tools": ["Read", "Write", "Bash"],
  "auto_approve": false
}
```

### Directory Structure

```
~/.ante/
├── settings.json        # User preferences
├── skills/              # User-level skills
└── agents/              # User-level sub-agents

.ante/                   # Project-local config
├── settings.json        # Project overrides
├── skills/
└── agents/
```

## CLI Commands

```bash
# Interactive mode
ante                        # Start REPL

# One-shot execution
ante run "prompt"          # Execute and exit

# Headless mode
ante task "task"           # Headless execution

# Session management
ante sessions              # List all sessions
ante resume <session-id>   # Resume session
ante export <session-id>   # Export session

# Configuration
ante config get model      # Get setting
ante config set model claude-opus-4.6  # Set
ante config reset          # Reset to defaults

# Info
ante version              # Version info
ante doctor               # Environment diagnostics
```

## Advanced Features

### Skills (Custom Capabilities)

Store custom skills for domain-specific operations:

```bash
~/.ante/skills/my_skill.md      # User-level
.ante/skills/deploy.md          # Project-level
```

Skills are discoverable and invokable as tools.

### Sub-Agents (Task Decomposition)

Spawn independent agents for parallel work:

```bash
# In ANTE prompt:
Use the Task tool to spawn a sub-agent for:
- Code generation
- Data analysis
- Testing
```

Sub-agents maintain isolated sessions and state.

### Memory

**Session Memory**: In-process context for current session.

**Long-term Memory**: Persistent across sessions with:
- Session transcripts
- Task summaries
- Semantic search
- Auto-compaction at context limits (10:1 compression)

### Offline Mode (Experimental)

Use local LLMs without internet:

```bash
ante run --provider local --model ggml-model.gguf "prompt"
```

## Integration Patterns

### With thegent

```yaml
# In thegent config
harnesses:
  ante:
    binary: /usr/local/bin/ante
    capabilities: [tui, headless, skills, sub_agents, memory]
    providers: [anthropic, openai, gemini, local]
    default_model: claude-opus-4.6
```

### Via Scripts/CI/CD

```bash
# Headless mode for CI
ante task "Run tests and report" \
  --provider openai \
  --model gpt-4o \
  --allowed-tools Bash,Read

# JSON output for parsing
ante run "..." --output json > result.json
```

### Custom Provider

Implement provider trait and register in catalog:

```rust
#[async_trait]
pub trait Provider: Send + Sync {
    async fn send(&self, req: ProviderRequest) -> Result<ProviderResponse>;
}
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| First Token | 200-800ms | Provider-dependent |
| Streaming | Real-time | Token-by-token delivery |
| Tool Overhead | <100ms | Most tools complete quickly |
| Process Memory | ~50-200MB | Baseline + per-session |
| Session Overhead | ~1-10MB | Per active session |
| Context Limit | ~100K tokens | Auto-compaction enabled |

## File Locations

| Location | Purpose |
|----------|---------|
| `~/.ante/settings.json` | User preferences |
| `~/.ante/skills/` | User-level skills |
| `~/.ante/agents/` | User-level sub-agents |
| `.ante/` | Project-local config |
| `.claude/` | Claude.ai compatibility |
| `/tmp/ante/` | Temporary files |

Override with: `ANTE_HOME=/custom/path`

## Key Concepts

**Session**: Isolated context. Each has independent state, memory, and configuration. Initialized with model/provider/policy.

**Task**: Unit of work within a session representing a user request or agent operation.

**Turn**: Individual exchange between user and agent with tool execution and state updates.

**Step**: Sub-operation within a turn (tool call, approval request, completion).

**Provider**: LLM abstraction layer. ANTE supports 6+ providers, making it model-agnostic.

**Tool**: Executable capability (file operations, shell, web, custom). Filterable and approvable.

**Skill**: Custom extension without modifying core. User or project-level.

**Sub-Agent**: Spawned agent instance for hierarchical task decomposition and parallel work.

## Comparison Matrix

| Feature | ANTE | Claude Code | Codex | Gemini CLI |
|---------|------|-------------|-------|-----------|
| Language | Rust | Go | Python | Go |
| Providers | 6+ | Anthropic | 3+ | Gemini |
| Offline Capable | Yes (exp) | Limited | Yes | No |
| Skills | Yes | Pattern-based | Yes | Limited |
| Sub-Agents | Yes | Yes | Yes | Limited |
| TUI | ratatui | CLI/panel | IDE | CLI |
| Maturity | Preview | Stable | Stable | Beta |
| Principle | Minimal core | IDE-first | Codex-centric | Gemini-centric |

## Resources

- **Docs**: https://docs.useante.com/
- **GitHub**: https://github.com/antigmaplex/ante
- **Antigma Labs**: https://antigmalabs.com/
- **Local Docs**: `/thegent/docs/context/ante/` (16 comprehensive guides)

## Status & Support

**Current Status**: Preview / Under Active Development

**Supported Platforms**: macOS, Linux (Windows TBD)

**Breaking Changes**: Expected during preview phase

**Community**: See GitHub issues and discussions

---

*Quick reference for ANTE terminal AI agent. For comprehensive documentation, see `/thegent/docs/context/ante/`.*
