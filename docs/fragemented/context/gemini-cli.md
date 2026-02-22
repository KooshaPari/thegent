# Gemini CLI Context

> Definitive reference for integrating Google Gemini CLI as an agent harness in thegent/CLIProxyAPIPlus.
> Sources: google-gemini/gemini-cli on GitHub, official documentation (fetched 2026-02-20).

---

## What is Gemini CLI

Gemini CLI is an open-source terminal-first AI agent that integrates Google's Gemini models directly into your command line. It provides lightweight access to Gemini's reasoning and tool-calling capabilities, designed for developers who work in the terminal.

Key characteristics:
- **Terminal-first design**: Full agent workflows in the CLI
- **Open source**: Apache 2.0 license
- **Multimodal support**: Code analysis, generation from prompts
- **Built-in tools**: Google Search (grounding), file operations, shell commands, web fetching
- **MCP extensible**: Custom integrations via Model Context Protocol
- **Free tier**: 60 requests/min, 1,000 requests/day with personal Google account
- **Paid tiers**: Available via Gemini API key or Vertex AI for enterprise

---

## Installation

### Via npm (Global)

```bash
npm install -g @google/gemini-cli
```

### Via Homebrew

```bash
brew install gemini-cli
```

### Via npx (No Installation)

```bash
npx @google/gemini-cli [args]
```

Verify installation:
```bash
gemini --version
```

---

## Authentication

Three authentication methods are supported:

| Method | Use Case | Setup |
|--------|----------|-------|
| **Google OAuth** | Individual developers, free tier | `gemini auth` → browser OAuth flow |
| **Gemini API Key** | Model selection, paid usage | `GEMINI_API_KEY=...` environment variable or `~/.gemini/config` |
| **Vertex AI** | Enterprise workloads, GCP integration | GCP service account credentials |

### OAuth Authentication

```bash
gemini auth
# Opens browser for Google OAuth, stores credentials locally in ~/.gemini/
```

### API Key Authentication

```bash
export GEMINI_API_KEY="your-api-key-here"
gemini --prompt "What is 2+2?"
```

### Vertex AI Authentication

Set up via GCP service account and environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
gemini --model gemini-2.0-flash-exp --prompt "Hello"
```

---

## Configuration

Config file location: `~/.gemini/config` (YAML or JSON format)

Alternatively, set `GEMINI_HOME` environment variable to use a custom config directory.

### Sample Configuration

```yaml
auth:
  method: api_key  # or oauth, vertex_ai
  api_key: your-api-key

models:
  default: gemini-2.0-flash
  experimental: gemini-2.0-flash-exp

tools:
  google_search:
    enabled: true
    max_results: 5
  file_operations:
    enabled: true
  shell_commands:
    enabled: true
    restricted: false
  web_fetch:
    enabled: true

sandbox:
  enabled: false  # Set true to enable sandbox mode by default
```

---

## CLI Flags and Modes

### Core Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--model` | `-m` | Model to use | `-m gemini-2.0-flash` |
| `--prompt` | `-p` | Provide prompt directly (non-interactive mode) | `-p "Analyze this code"` |
| `--non-interactive` | `-n` | Run without interactivity | Implicit with `--prompt` |
| `--yolo` | | Enable YOLO mode (auto-approve all tool calls) | `--yolo` |
| `--approval-mode` | | Set approval behavior | `--approval-mode=yolo` or `--approval-mode=manual` |
| `--sandbox` | | Enable sandbox mode for this session | `--sandbox` |
| `--help` | `-h` | Show help | `gemini --help` |
| `--version` | `-v` | Show version | `gemini --version` |

### Interactive Mode (Default)

```bash
gemini
```

Starts an interactive session. The model waits for user approval before executing tool calls unless `--yolo` is set.

### Non-Interactive Mode

```bash
gemini --prompt "Write a Python function that calculates Fibonacci"
gemini -p "Explain this code" < code.py
```

Passes prompt directly, executes in non-interactive mode. Returns response and exits.

### YOLO Mode

```bash
gemini --yolo
# or during session: press Ctrl+Y
```

Automatically approves all tool calls without user confirmation. Useful for:
- CI/CD pipelines
- Automated scripts
- Unattended execution

**Note**: YOLO mode automatically enables sandbox mode by default for security.

### Sandbox Mode

```bash
gemini --sandbox
```

Restricts tool execution within a sandboxed environment. Tool calls are isolated and cannot access system resources outside the sandbox.

### Model Selection

```bash
gemini --model gemini-2.0-flash
gemini -m gemini-2.0-flash-exp
```

Available models (as of 2026-02-20):
- `gemini-2.0-flash` (stable, recommended)
- `gemini-2.0-flash-exp` (experimental, latest features)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

---

## Built-in Tools

Gemini CLI provides native integration with several tools without custom MCP configuration:

### Google Search (Grounding)

Enable real-time web search results in model context:

```bash
gemini --prompt "Latest news about AI in 2026"
# Model has access to current web search results
```

### File Operations

Read, write, and manipulate files:

```bash
gemini --prompt "Analyze file contents" < data.csv
```

Configuration in `~/.gemini/config`:
```yaml
tools:
  file_operations:
    enabled: true
```

### Shell Commands

Execute shell commands (with approval):

```bash
# Interactive: model suggests commands, you approve
gemini --prompt "Show me the top 10 largest files in this directory"

# YOLO mode: auto-execute commands
gemini --yolo --prompt "List all Python files and count lines"
```

### Web Fetching

Retrieve and analyze web content:

```bash
gemini --prompt "Summarize this article: https://example.com/article"
```

---

## MCP (Model Context Protocol) Support

Gemini CLI supports MCP for extending capabilities with custom tools and resources.

### Using MCP Servers

Configure MCP servers in `~/.gemini/config`:

```yaml
mcp:
  servers:
    - name: custom-tools
      command: python /path/to/mcp_server.py
      transport: stdio
    - name: web-search
      command: npx web-search-mcp
      transport: stdio
    - name: database
      url: http://localhost:3000
      transport: sse
```

### Transport Types Supported

- **STDIO** (default): Subprocess-based communication
- **SSE**: HTTP Server-Sent Events for remote servers
- **HTTP**: Streamable HTTP transport

### Example: Custom MCP Tool

Create `custom_mcp_server.py`:

```python
#!/usr/bin/env python3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, ToolCall

server = Server("custom-tools")

@server.tool("calculate_md5")
def calculate_md5(text: str) -> str:
    """Calculate MD5 hash of text."""
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()

# Register and serve
if __name__ == "__main__":
    import asyncio
    with stdio_server(server) as streams:
        asyncio.run(server.run(streams[0], streams[1]))
```

Then use in Gemini CLI:
```bash
gemini --prompt "Calculate MD5 hash of 'hello world'"
# Gemini will use the custom tool
```

---

## Non-Interactive / Subprocess Invocation

For automation, CI/CD, and programmatic use:

```bash
#!/bin/bash
# Single prompt, exit after response
gemini --prompt "Generate a test file for this code" < src/main.py > output.txt

# Chain multiple invocations
output=$(gemini -p "Explain this error" 2>&1 <<< "$error_message")
echo "Analysis: $output"

# With YOLO mode in scripts
gemini --yolo -p "Refactor this code for performance" < code.js

# Export results
gemini -p "Generate CSV report" --output json > report.json
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 127 | Command not found |

### Subprocess Best Practices

- Use `--prompt` (or `-p`) for direct input
- Combine with `--yolo` for auto-approval
- Use `--model` to specify model explicitly
- Pipe input via stdin when appropriate
- Capture stdout for automation
- Log stderr for debugging

---

## Comparison to Other Harnesses

### vs. Codex

| Aspect | Gemini CLI | Codex |
|--------|-----------|-------|
| **Model** | Google Gemini 2.0 | OpenAI GPT-5.3 |
| **Open Source** | Yes (Apache 2.0) | No |
| **CLI-first** | Yes | Yes, but Codex is API-first |
| **Tool Support** | MCP extensible | OpenAI tools native |
| **Free Tier** | Yes (1K req/day) | No free tier |
| **Reasoning** | Gemini 2.0 advanced reasoning | GPT-5.3 built-in reasoning |
| **Speed** | Fast (optimized for CLI) | Very fast (API optimized) |

### vs. Claude Code

| Aspect | Gemini CLI | Claude Code |
|--------|-----------|-----------|
| **Interface** | Terminal CLI only | IDE plugin + terminal |
| **Model** | Google Gemini 2.0 | Anthropic Claude |
| **Authentication** | OAuth or API key | Claude API key |
| **Ecosystem** | Google Cloud focused | Anthropic SDK focused |
| **Built-in Tools** | Search, files, shell | Advanced reasoning, artifacts |

### vs. Local Models

| Aspect | Gemini CLI | Local (Ollama, GGUF) |
|--------|-----------|----------------------|
| **Latency** | ~500ms (API call) | <100ms (local) |
| **Cost** | Pay per request | Free (local compute) |
| **Capability** | State-of-the-art | Smaller, less capable |
| **Authentication** | Cloud auth required | None |
| **Data Privacy** | Google-hosted | Complete local privacy |

---

## Thegent Integration

Gemini CLI can be registered as an alternative harness in thegent's provider registry:

### Registration

In thegent's harness registry (`providers/registry.yaml` or equivalent):

```yaml
harnesses:
  gemini:
    name: "Google Gemini CLI"
    executable: "gemini"
    api_type: "subprocess_cli"
    auth_methods:
      - oauth
      - api_key
      - vertex_ai
    models:
      - gemini-2.0-flash
      - gemini-2.0-flash-exp
      - gemini-1.5-pro
    tool_support: mcp
    min_version: "0.11.0"
    config_path: "~/.gemini/config"
```

### CLI-to-APIPlus Bridge

To expose Gemini CLI via thegent's OpenAI-compatible proxy at localhost:8317:

```python
# In CLIProxyAPIPlus routing layer
class GeminiCLIHandler(CLIHandler):
    def call(self, messages: List[Dict], model: str, **kwargs):
        prompt = self._format_messages(messages)
        result = subprocess.run(
            ["gemini", "--prompt", prompt, "--model", model, "--yolo"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return self._parse_response(result.stdout)
```

### Features via Proxy

- Model selection: `POST /v1/chat/completions` with `model: "gemini/gemini-2.0-flash"`
- Tool calling: Routed through MCP servers declared in `~/.gemini/config`
- Streaming: Via subprocess output streaming
- Cost tracking: Integration with Gemini API quota metrics

---

## Release Schedule and Versions

**Release Cycle**: Weekly stable releases on Tuesdays at 2000 UTC

- **Stable Tag**: Each week's promotion of previous week's preview release + bug fixes
- **Preview Tag**: Experimental features available before stable
- **Recommendation**: Always use the latest stable tag

Check releases: `gemini --version` or visit GitHub releases.

---

## Key Differences from OpenAI / Anthropic APIs

| Area | Gemini CLI | OpenAI API | Anthropic API |
|------|-----------|-----------|--------------|
| **Invocation** | Subprocess CLI | HTTP REST | HTTP REST |
| **Models** | Gemini 2.0 family | GPT-4, GPT-5 family | Claude family |
| **Authentication** | OAuth, API key, Vertex AI | API key only | API key only |
| **Tool Protocol** | MCP | OpenAI native tools | Tool use protocol |
| **Reasoning Access** | Gemini 2.0 reasoning | Extended thinking (o1, o3) | Built-in, no opt-in |
| **State Management** | Manual (session-based) | Manual (messages array) | Manual (messages array) |

---

## Sources

- [Google Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Official Documentation](https://google-gemini.github.io/gemini-cli/)
- [Gemini CLI Releases](https://github.com/google-gemini/gemini-cli/releases)
- [Gemini CLI Configuration Guide](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html)
- [Gemini CLI Tutorial: Command Line Parameters](https://medium.com/google-cloud/gemini-cli-tutorial-series-part-2-gemini-cli-command-line-parameters-e64e21b157be)
- [Model Context Protocol (MCP) Integration](https://modelcontextprotocol.io/)
