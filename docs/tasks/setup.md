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

1. **Dependencies**: Installs system dependencies via Homebrew
2. **Python Environment**: Sets up Python virtual environment with `uv sync`
3. **Configuration**: Creates `.env` file from `.env.example` if it doesn't exist
4. **CLIProxy**: Builds and configures CLIProxyAPIPlus
5. **Polyglot Setup**: Sets up multi-runtime support (PyPy, CPython, Rust, Go)
6. **Shims**: Installs tool shims to `~/.local/bin`
7. **Shell Integration**: Configures shell integration
8. **Health Check**: Runs `thegent doctor` to verify setup

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
