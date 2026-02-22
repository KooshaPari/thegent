# Merged Fragmented Markdown

## Source: tasks/doctor.md

# Task: doctor

## Description

Run comprehensive health checks and diagnostics for the thegent environment.

## Usage

```bash
task doctor
task doctor --fix
```

## Examples

```bash
# Basic health check
task doctor

# Health check with automatic fixes
task doctor --fix

# Multi-runtime diagnostics
uv run thegent doctor --runtime

# Network diagnostics
uv run thegent doctor --network

# Toolchain manager sanity checks
mise doctor
uv --version
brew bundle check
```

## What It Checks

1. **Dependencies**: Node.js, Claude Code CLI, Codex CLI, CLIProxyAPIPlus, tools (git, rg, fd, jq)
2. **Configuration**: Environment variables, config files
3. **Isolation**: Process isolation, resource limits
4. **Connectivity**: MCP server connectivity, network access
5. **Environment**: PATH setup, shims installation
6. **Shim Binaries**: Binary availability and correctness
7. **Shell**: Shell integration (zsh, bash)
8. **Nix Support**: Nix environment if available
9. **Providers**: Provider configuration and authentication
10. **Runtime Infrastructure**: Resource monitoring, process registry
11. **Process Leaks**: Zombie processes, resource leaks
12. **MCP Tools**: MCP server tools availability
13. **Sessions**: Active session health
14. **Performance**: Performance bottlenecks

## Options

- `--fix`: Attempt to automatically fix detected issues
- `--runtime`: Show multi-runtime diagnostics (PyPy, CPython, Rust, Go, Mojo, Zig)
- `--network`: Check network connectivity
- `--processes`: Check process health
- `--memory`: Check memory usage
- `--deps`: Check dependencies

## Common Issues

### MCP Server Not Running

**Problem**: Cannot connect to MCP server.

**Solution**:
```bash
# Start MCP server
task dev

# Or manually
uv run thegent mcp up
```

### Shim PATH Issues

**Problem**: Shims not found in PATH.

**Solution**:
```bash
# Ensure ~/.local/bin is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $PATH | grep -q ".local/bin" && echo "OK" || echo "Not in PATH"
```

### Missing Dependencies

**Problem**: Required tools not found.

**Solution**:
```bash
# Install via Homebrew (macOS)
brew install git ripgrep fd jq

# Or via package manager (Linux)
sudo apt-get install git ripgrep fd-find jq
```

### Manager Drift

**Problem**: Runtime versions or tooling differ across devices.

**Solution**:
```bash
# Validate runtime pins and shell activation
mise doctor
mise current

# Validate Python tooling path/version
uv --version
uv run python --version

# Validate host package set (macOS)
brew bundle check
```

## Related Tasks

- `task setup` - Initial setup
- `task dev` - Start development environment
- `task polyglot:doctor` - Polyglot-specific diagnostics

## Time Estimate

- Basic check: 10-30 seconds
- Full check with fixes: 30-60 seconds
- With multi-runtime diagnostics: 1-2 minutes

---

## Source: tasks/setup.md

# Task: setup

## Description

Full setup: dependencies, configuration, shell, shims, and polyglot runtime setup.

## Usage

```bash
task setup
```

## Examples

```bash
# Full setup (recommended for first-time setup)
task setup

# Setup without polyglot (if you don't need multi-runtime support)
task setup --no-polyglot
```

## What It Does

1. **Dependencies**: Installs system dependencies via package manager (Homebrew on macOS via `Brewfile`)
2. **Python Environment**: Sets up Python virtual environment with `uv sync`
3. **Configuration**: Creates `.env` file from `.env.example` if it doesn't exist
4. **CLIProxy**: Builds and configures CLIProxyAPIPlus
5. **Polyglot Setup**: Sets up multi-runtime support (PyPy, CPython, Rust, Go)
6. **Shims**: Installs tool shims to `~/.local/bin`
7. **Shell Integration**: Configures shell integration
8. **Health Check**: Runs `thegent doctor` to verify setup

Runtime policy note:

- Prefer `mise` for runtime version pinning (`.mise.toml`) and `uv` for Python dependencies.
- `task setup` remains the canonical project bootstrap entrypoint.

## Dependencies

- `cliproxy:build`
- `cliproxy:ensure-config`
- `polyglot:setup`
- `shims:guard`
- `shims:probe`

## Common Issues

### Homebrew Not Found

**Problem**: `brew bundle` fails because Homebrew is not installed.

**Solution**:
```bash
# Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### uv Not Found

**Problem**: `uv sync` fails because `uv` is not installed.

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Permission Denied for ~/.local/bin

**Problem**: Cannot write to `~/.local/bin`.

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p ~/.local/bin
chmod 755 ~/.local/bin
```

## Related Tasks

- `task dev` - Start development environment
- `task doctor` - Verify environment health
- `task polyglot:setup` - Setup polyglot runtimes only
- `task shims:guard` - Validate shims

## Time Estimate

- First run: 5-10 minutes (depending on internet speed)
- Subsequent runs: 1-2 minutes (if dependencies are cached)

---
