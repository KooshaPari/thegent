# Merged Fragmented Markdown

## Source: tutorials/01-quick-start.md

# Tutorial 1: Quick Start

Get thegent up and running in 5 minutes.

## Prerequisites

- Python 3.10+
- Rust (for high-performance extensions)
- Homebrew (macOS) or package manager (Linux)

## Step 1: Installation

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

### From Source

```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
```

## Step 2: Setup

Run the interactive setup wizard:

```bash
thegent setup --wizard
```

This will guide you through:
1. Basic configuration (MCP host, port, directories)
2. Model defaults (Cursor, Gemini, Copilot, Claude, Codex)
3. Performance settings (timeouts, routing)
4. Budget settings (optional)
5. Advanced settings (optional)

Or use defaults:

```bash
thegent setup
```

## Step 3: Verify Installation

Check that everything is set up correctly:

```bash
thegent doctor
```

You should see:
- ✓ All dependencies installed
- ✓ Configuration valid
- ✓ MCP server accessible
- ✓ Shims installed

## Step 4: Run Your First Agent

```bash
thegent run "Analyze the current directory structure" free
```

This runs a free agent (Copilot) to analyze your directory.

## Step 5: Check Status

```bash
thegent ps
```

This shows active and historical agent sessions.

## Next Steps

- [Configuration Tutorial](./02-configuration.md) - Customize your setup
- [First Agent Run](./03-first-agent-run.md) - Learn about agent execution
- [Multi-Agent Workflows](./04-multi-agent-workflows.md) - Orchestrate multiple agents

## Troubleshooting

If you encounter issues:

1. Run `thegent doctor` to diagnose problems
2. Check [Troubleshooting Guide](../guides/TROUBLESHOOTING.md)
3. Run `thegent doctor --fix` to attempt automatic fixes

## Common Issues

### Command Not Found

If `thegent` command is not found:

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### MCP Server Not Running

```bash
# Start MCP server
thegent mcp up

# Or use task
task dev
```

### Configuration Errors

```bash
# Validate configuration
thegent config validate

# Run wizard again
thegent config wizard
```

## Success!

You're now ready to use thegent! Continue to the next tutorial to learn about configuration.

---

## Source: tutorials/02-configuration.md

# Tutorial 2: Configuration

Learn how to configure thegent for your specific needs.

## Overview

Thegent uses a `.env` file for configuration. You can:
- Use the interactive wizard (`thegent config wizard`)
- Edit `.env` directly
- Use environment variables

## Configuration Wizard

The easiest way to configure thegent:

```bash
thegent config wizard
```

This interactive wizard guides you through:
1. Basic settings (MCP host, port, directories)
2. Model defaults
3. Performance settings
4. Budget settings
5. Advanced settings

## Manual Configuration

Edit `.env` file directly:

```bash
# Basic Configuration
THGENT_MCP_HOST=127.0.0.1
THGENT_MCP_PORT=3847
THGENT_SESSION_DIR=~/.cache/thegent/sessions
THGENT_CACHE_DIR=~/.cache/thegent

# Model Defaults
THGENT_DEFAULT_CURSOR_MODEL=gemini-3-flash
THGENT_DEFAULT_GEMINI_MODEL=gemini-3-flash
THGENT_DEFAULT_COPILOT_MODEL=gpt-5-mini
THGENT_DEFAULT_CLAUDE_MODEL=claude-opus-4.6
THGENT_DEFAULT_CODEX_MODEL=gpt-5.3-codex-spark

# Performance
THGENT_DEFAULT_TIMEOUT=1800
THGENT_MAX_IDLE_SECONDS=180
THGENT_DEFAULT_ROUTING=prefer_direct

# Budget (optional)
THGENT_BUDGET_HOURLY_LIMIT=10.0
THGENT_BUDGET_DAILY_LIMIT=100.0
THGENT_BUDGET_RUN_LIMIT=5.0
```

## Environment Variables

You can also set configuration via environment variables:

```bash
export THGENT_MCP_HOST=127.0.0.1
export THGENT_MCP_PORT=3847
thegent run "test"
```

Environment variables take precedence over `.env` file.

## Validation

Validate your configuration:

```bash
thegent config validate
```

This checks:
- Required settings are present
- Values are within valid ranges
- File paths exist or can be created
- Model names are valid

## Configuration Migration

Migrate from old configuration format:

```bash
thegent config migrate --source .env.old --target .env.new --dry-run
```

Review the migration, then apply:

```bash
thegent config migrate --source .env.old --target .env.new
```

## Viewing Configuration

Show current configuration:

```bash
thegent config show
```

This displays:
- Current settings
- Source (env file or default)
- Resolved values

## Common Settings

### MCP Server

```bash
THGENT_MCP_HOST=127.0.0.1
THGENT_MCP_PORT=3847
```

### Timeouts

```bash
# Default timeout (30 minutes)
THGENT_DEFAULT_TIMEOUT=1800

# Max idle time (3 minutes)
THGENT_MAX_IDLE_SECONDS=180
```

### Routing

```bash
# Options: prefer_direct, prefer_proxy, failover
THGENT_DEFAULT_ROUTING=prefer_direct
```

### Budget Limits

```bash
THGENT_BUDGET_HOURLY_LIMIT=10.0
THGENT_BUDGET_DAILY_LIMIT=100.0
THGENT_BUDGET_RUN_LIMIT=5.0
THGENT_BUDGET_WARNING_THRESHOLD=0.8
```

## Environment-Specific Configs

Use different configs for different environments:

```bash
# Development
thegent config wizard --config .env.development

# Production
thegent config wizard --config .env.production

# Use specific config
THGENT_ENV_FILE=.env.production thegent run "test"
```

## Next Steps

- [First Agent Run](./03-first-agent-run.md) - Run your first agent
- [Performance Optimization](./08-performance-optimization.md) - Optimize settings
- [Governance & Policies](./09-governance-policies.md) - Set up governance

## Troubleshooting

### Invalid Configuration

```bash
# Validate and see errors
thegent config validate

# Fix issues
thegent config wizard
```

### Configuration Not Loading

```bash
# Check file exists
ls -la .env

# Check permissions
chmod 644 .env

# Verify format
cat .env | grep THGENT_
```

---
