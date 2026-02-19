# mise Installation Integration - Complete

## Status: ✅ Complete

Both `thegent setup` and `thegent install` now support system-wide mise installation via Homebrew or Nix.

## Commands Configured

### 1. `thegent setup`
```bash
thegent setup --system-deps          # Install mise via Homebrew
thegent setup --system-deps --nix    # Install mise via Nix
```

**Parameters added:**
- `--system-deps`: Install system dependencies (Homebrew, mise, git repos)
- `--nix`: Use Nix for mise installation instead of Homebrew

**Location:** `src/thegent/cli.py:6860`

### 2. `thegent install`
```bash
thegent install --system-deps          # Install mise via Homebrew
thegent install --system-deps --nix    # Install mise via Nix
```

**Parameters added:**
- `--system-deps`: Install system dependencies (Homebrew, mise, git repos)
- `--nix`: Use Nix for mise installation instead of Homebrew

**Location:** `src/thegent/main.py:4567`

## What Gets Installed

When `--system-deps` is used:

1. **Homebrew** (if missing)
   - Installs via official script
   - Adds to PATH on Apple Silicon Macs

2. **mise** (if missing)
   - Via Homebrew: `brew install mise`
   - Via Nix (with `--nix`): `nix profile install nixpkgs#mise`
   - **Automatically configures shell hooks** in `.zshenv` or `.zshrc`
   - Places mise hooks BEFORE direnv hooks for precedence

3. **Git Repositories** (optional, via `git_repos` parameter)
   - Can clone repos with optional branch specification

## Shell Hook Auto-Installation

When mise is installed, the installer automatically:

1. Detects shell type (zsh, bash, etc.)
2. Finds appropriate config file (`.zshenv` preferred, falls back to `.zshrc`)
3. Adds mise hook if not already present
4. Places mise hook before direnv hook (if direnv exists)
5. Sets `MISE_ENV=1` so direnv knows to skip

**Implementation:** `src/thegent/install.py:install_mise()`

## Usage Examples

### Basic Setup with mise
```bash
# Install mise and configure shell hooks
thegent setup --system-deps

# Or use Nix
thegent setup --system-deps --nix
```

### Full Installation with mise
```bash
# Install mise + all thegent components
thegent install --system-deps

# With Nix
thegent install --system-deps --nix

# Dry run to see what would happen
thegent install --system-deps --dry-run
```

### Verify Installation
```bash
# Check if mise is installed
mise --version

# Check if mise hooks are configured
grep "mise activate" ~/.zshenv ~/.zshrc

# Check if mise is active
echo $MISE_ENV  # Should output "1" if active
```

## Integration Points

### Code Flow

1. **User runs:** `thegent setup --system-deps` or `thegent install --system-deps`

2. **Function calls:**
   - `setup_cmd()` or `install_cmd()` receives `system_deps=True`
   - Calls `install_system_dependencies()` from `install.py`
   - Which calls `install_mise()` with `use_nix` flag

3. **mise installation:**
   - Checks if mise already installed
   - Installs via Homebrew or Nix
   - Auto-configures shell hooks
   - Returns success/failure status

### Files Modified

- ✅ `src/thegent/cli.py` - Added `system_deps` and `use_nix` to `setup_cmd()`
- ✅ `src/thegent/main.py` - Added `system_deps` and `use_nix` to `install_cmd()`
- ✅ `src/thegent/install.py` - Added `install_mise()` with auto hook configuration
- ✅ `src/thegent/install.py` - Added `install_system_dependencies()` orchestrator

## Testing

To test the integration:

```bash
# Test setup command
thegent setup --system-deps --dry-run

# Test install command  
thegent install --system-deps --dry-run

# Verify parameters are available
thegent setup --help | grep system-deps
thegent install --help | grep system-deps
```

## Next Steps

1. ✅ Parameters added to both commands
2. ✅ mise installation function implemented
3. ✅ Shell hook auto-configuration implemented
4. ✅ Nix support added
5. ✅ Documentation created

**Status: Ready for use!**
